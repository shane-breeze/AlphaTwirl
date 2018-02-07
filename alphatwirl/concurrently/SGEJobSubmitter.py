#!/usr/bin/env python
# Tai Sakuma <sakuma@cern.ch>
import os
import sys
import argparse
import shlex
import subprocess
import collections
import time as t
import textwrap
import getpass
import re
import logging

import alphatwirl

##__________________________________________________________________||
SGE_JOBSTATUS = {
    1: "Failed",
    2: "Pending",
}

##__________________________________________________________________||
class SGEJobSubmitter(object):
    def __init__(self, queue="hep.q", time=10800):
        self.job_desc_template = "qsub -o {out} -e {error} -cwd -V -q {queue} -l h_rt={time} {job_script}"
        self.clusterids_outstanding = [ ]
        self.clusterids_finished = [ ]
        self.queue = queue
        self.time = time

    def run(self, workingArea, package_index):

        cwd = os.getcwd()
        os.chdir(workingArea.path)

        package_path = workingArea.package_path(package_index)

        resultdir_basename = os.path.splitext(package_path)[0]
        resultdir_basename = os.path.splitext(resultdir_basename)[0]
        resultdir = os.path.join('results', resultdir_basename)
        alphatwirl.mkdir_p(resultdir)

        input_files = [package_path, 'python_modules.tar.gz']
        input_files = [f for f in input_files if os.path.exists(f)]

        job_desc = self.job_desc_template.format(
            job_script = 'job_script.sh',
            out = os.path.join(resultdir, 'stdout.txt'),
            error = os.path.join(resultdir, 'stderr.txt'),
            queue = self.queue,
            time = self.time,
        )

        with open("job_script.sh",'w') as f:
            f.write("python {job_script} {args}".format(job_script="run.py",
                                                        args=package_path))

        proc = subprocess.Popen(
            job_desc.split(),
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()

        regex = re.compile("Your job (\d*)", re.MULTILINE)
        clusterid = regex.search(stdout).groups()[0]

        self.clusterids_outstanding.append(clusterid)

        #change_job_priority([clusterid], 10) ## need to make configurable

        os.chdir(cwd)

        return clusterid

    def poll(self):
        """check if the jobs are running and return a list of cluster IDs for
        finished jobs

        """

        clusterid_status_list = query_status_for(self.clusterids_outstanding)
        # e.g., [['1730126', 2], ['1730127', 2], ['1730129', 1], ['1730130', 1]]


        if clusterid_status_list:
            clusterids, statuses = zip(*clusterid_status_list)
        else:
            clusterids, statuses = (), ()

        clusterids_finished = [i for i in self.clusterids_outstanding if i not in clusterids]
        self.clusterids_finished.extend(clusterids_finished)
        self.clusterids_outstanding[:] = clusterids

        # logging
        counter = collections.Counter(statuses)
        messages = [ ]
        if counter:
            messages.append(', '.join(['{}: {}'.format(SGE_JOBSTATUS[k], counter[k]) for k in counter.keys()]))
        if self.clusterids_finished:
            messages.append('Finished {}'.format(len(self.clusterids_finished)))
        logger = logging.getLogger(__name__)
        logger.info(', '.join(messages))

        return clusterids_finished

    def wait(self):
        """wait until all jobs finish and return a list of cluster IDs
        """
        sleep = 5
        while self.clusterids_outstanding:
            self.poll()
            t.sleep(sleep)
        return self.clusterids_finished

    def failed_runids(self, runids):
        # remove failed clusterids from self.clusterids_finished
        # so that len(self.clusterids_finished)) becomes the number
        # of the successfully finished jobs
        for i in runids:
            try:
                self.clusterids_finished.remove(i)
            except ValueError:
                pass

    def terminate(self):
        n_at_a_time = 500
        ids_split = [self.clusterids_outstanding[i:(i + n_at_a_time)] for i in range(0, len(self.clusterids_outstanding), n_at_a_time)]
        statuses = [ ]
        for ids_sub in ids_split:
            procargs = ['qdel'] + ids_sub
            stdout = try_executing_until_succeed(procargs)

##__________________________________________________________________||
def try_executing_until_succeed(procargs):

    sleep = 2
    logger = logging.getLogger(__name__)

    while True:

        # logging
        ellipsis = '...(({} letters))...'
        nfirst = 50
        nlast = 50
        command_display = '{} {}'.format(procargs[0], ' '.join([repr(a) for a in procargs[1:]]))
        if len(command_display) > nfirst + len(ellipsis) + nlast:
            command_display = '{}...(({} letters))...{}'.format(
                command_display[:nfirst],
                len(command_display) - (nfirst + nlast),
                command_display[-nlast:]
            )
        logger.debug('execute: {}'.format(command_display))

        #
        proc = subprocess.Popen(
            procargs,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr =  proc.communicate()
        success = not (proc.returncode or stderr) or "not exist" in stderr

        #
        if success: break

        #
        if stderr: logger.warning(stderr.strip())
        logger.warning('the command failed: {}. will try again in {} seconds'.format(command_display, sleep))

        #
        t.sleep(sleep)

    if "not exist" in stderr: return [ ]
    elif "error state" in stdout: retval = "{} 1".format(procargs[-1])
    else: retval = "{} 2".format(procargs[-1])
    return [retval]

##__________________________________________________________________||
def query_status_for(ids):

    n_at_a_time = 1#500
    ids_split = [ids[i:(i + n_at_a_time)] for i in range(0, len(ids), n_at_a_time)]
    stdout = [ ]
    for ids_sub in ids_split:
        procargs = ['qstat', '-j'] + ids_sub
        stdout.extend(try_executing_until_succeed(procargs))

    # e.g., stdout = ['688244 1 ', '688245 1 ', '688246 2 ']

    ret = [l.strip().split() for l in stdout]
    # e.g., [['688244', '1'], ['688245', '1'], ['688246', '2']]

    ret = [[e[0], int(e[1])] for e in ret]
    # a list of [clusterid, status]
    # e.g., [['688244', 1], ['688245', 1], ['688246', 2]]

    return ret

#  ##__________________________________________________________________||
#  def change_job_priority(ids, priority=10):
#
#      # http://research.cs.wisc.edu/htcondor/manual/v7.8/2_6Managing_Job.html#sec:job-prio
#
#      n_at_a_time = 500
#      ids_split = [ids[i:(i + n_at_a_time)] for i in range(0, len(ids), n_at_a_time)]
#      for ids_sub in ids_split:
#          procargs = ['condor_prio', '-p', str(priority)] + ids_sub
#          try_executing_until_succeed(procargs)

##__________________________________________________________________||
