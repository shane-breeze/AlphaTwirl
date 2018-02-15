#!/usr/bin/env python
# Tai Sakuma <sakuma@cern.ch>
import os, sys
import subprocess
import collections
import time
import textwrap
import getpass
import re
import logging

import alphatwirl

from .exec_util import try_executing_until_succeed, compose_shortened_command_for_logging

##__________________________________________________________________||
# https://htcondor-wiki.cs.wisc.edu/index.cgi/wiki?p=MagicNumbers
HTCONDOR_JOBSTATUS = {
    0: "Unexpanded",
    1: "Idle",
    2: "Running",
    3: "Removed",
    4: "Completed",
    5: "Held",
    6: "Transferring_Output",
    7: "Suspended"
}

##__________________________________________________________________||
class HTCondorJobSubmitter(object):
    def __init__(self, job_desc_extra=[ ]):

        self.job_desc_template = """
        Executable = run.py
        output = results/$(resultdir)/stdout.txt
        error = results/$(resultdir)/stderr.txt
        log = results/$(resultdir)/log.txt
        Arguments = $(resultdir).p.gz
        should_transfer_files = YES
        when_to_transfer_output = ON_EXIT
        transfer_input_files = {input_files}
        transfer_output_files = results
        Universe = vanilla
        notification = Error
        getenv = True
        queue resultdir in {resultdirs}
        """
        self.job_desc_template = textwrap.dedent(self.job_desc_template).strip()

        if job_desc_extra:
            lines = self.job_desc_template.split('\n')
            lines[-1:-1] = job_desc_extra
            self.job_desc_template = '\n'.join(lines)

        self.clusterprocids_outstanding = [ ]
        self.clusterprocids_finished = [ ]

    def run(self, workingArea, package_index):
        return self.run_multiple(workingArea, [package_index])[0]

    def run_multiple(self, workingArea, package_indices):

        if not package_indices:
            return [ ]

        cwd = os.getcwd()
        os.chdir(workingArea.path)

        package_paths = [workingArea.package_path(i) for i in package_indices]
        resultdir_basenames = [os.path.splitext(p)[0] for p in package_paths]
        resultdir_basenames = [os.path.splitext(n)[0] for n in resultdir_basenames]
        resultdirs = [os.path.join('results', n) for n in resultdir_basenames]

        for d in resultdirs:
            alphatwirl.mkdir_p(d)

        extra_input_files = ['python_modules.tar.gz']
        extra_input_files = [f for f in extra_input_files if os.path.exists(f)]

        job_desc = self.job_desc_template.format(
            input_files = ', '.join(['$(resultdir).p.gz'] + extra_input_files),
            resultdirs = ', '.join(resultdir_basenames)
        )

        procargs = ['condor_submit']

        logger = logging.getLogger(__name__)
        command_display = compose_shortened_command_for_logging(procargs)
        logger.debug('execute: {!r}'.format(command_display))

        proc = subprocess.Popen(
            procargs,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = proc.communicate(job_desc)
        stdout = stdout.decode()
        stderr = stderr.decode()

        for l in stdout.rstrip().split('\n'):
            logger.debug(l)

        regex = re.compile("(\d+) job\(s\) submitted to cluster (\d+)", re.MULTILINE)
        njobs = int(regex.search(stdout).groups()[0])
        clusterid = regex.search(stdout).groups()[1]
        # e.g., '3158626'

        change_job_priority([clusterid], 10) ## need to make configurable

        procid = ['{}'.format(i) for i in range(njobs)]
        # e.g., ['0', '1', '2', '3']

        clusterprocids = ['{}.{}'.format(clusterid, i) for i in procid]
        # e.g., ['3158626.0', '3158626.1', '3158626.2', '3158626.3']

        self.clusterprocids_outstanding.extend(clusterprocids)

        os.chdir(cwd)

        return clusterprocids

    def poll(self):
        """check if the jobs are running and return a list of cluster IDs for
        finished jobs

        """

        clusterids = clusterprocids2clusterids(self.clusterprocids_outstanding)
        clusterprocid_status_list = query_status_for(clusterids)
        # e.g., [['1730126.0', 2], ['1730127.0', 2], ['1730129.1', 1], ['1730130.0', 1]]


        if clusterprocid_status_list:
            clusterprocids, statuses = zip(*clusterprocid_status_list)
        else:
            clusterprocids, statuses = (), ()

        clusterprocids_finished = [i for i in self.clusterprocids_outstanding if i not in clusterprocids]
        self.clusterprocids_finished.extend(clusterprocids_finished)
        self.clusterprocids_outstanding[:] = clusterprocids

        # logging
        counter = collections.Counter(statuses)
        messages = [ ]
        if counter:
            messages.append(', '.join(['{}: {}'.format(HTCONDOR_JOBSTATUS[k], counter[k]) for k in counter.keys()]))
        if self.clusterprocids_finished:
            messages.append('Finished {}'.format(len(self.clusterprocids_finished)))
        logger = logging.getLogger(__name__)
        logger.info(', '.join(messages))

        return clusterprocids_finished

    def wait(self):
        """wait until all jobs finish and return a list of cluster IDs
        """
        sleep = 5
        while self.clusterprocids_outstanding:
            self.poll()
            time.sleep(sleep)
        return self.clusterprocids_finished

    def failed_runids(self, runids):
        # remove failed clusterprocids from self.clusterprocids_finished
        # so that len(self.clusterprocids_finished)) becomes the number
        # of the successfully finished jobs
        for i in runids:
            try:
                self.clusterprocids_finished.remove(i)
            except ValueError:
                pass

    def terminate(self):
        clusterids = clusterprocids2clusterids(self.clusterprocids_outstanding)
        ids_split = split_ids(clusterids)
        statuses = [ ]
        for ids_sub in ids_split:
            procargs = ['condor_rm'] + ids_sub
            command_display = compose_shortened_command_for_logging(procargs)
            logger = logging.getLogger(__name__)
            logger.debug('execute: {}'.format(command_display))
            proc = subprocess.Popen(
                procargs,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate()

##__________________________________________________________________||
def clusterprocids2clusterids(clusterprocids):
    return list(set([i.split('.')[0] for i in clusterprocids]))

##__________________________________________________________________||
def query_status_for(ids, n_at_a_time=500):

    ids_split = split_ids(ids, n=n_at_a_time)
    stdout = [ ]
    for ids_sub in ids_split:
        procargs = ['condor_q'] + ids_sub + ['-format', '%d.', 'ClusterId', '-format', '%d ', 'ProcId', '-format', '%-2s\n', 'JobStatus']
        stdout.extend(try_executing_until_succeed(procargs))

    # e.g., stdout = ['688244.0 1 ', '688245.0 1 ', '688246.0 2 ']

    ret = [l.strip().split() for l in stdout]
    # e.g., [['688244.0', '1'], ['688245.0', '1'], ['688246.0', '2']]

    ret = [[e[0], int(e[1])] for e in ret]
    # a list of [clusterprocid, status]
    # e.g., [['688244.0', 1], ['688245.0', 1], ['688246.0', 2]]

    return ret

##__________________________________________________________________||
def change_job_priority(ids, priority=10, n_at_a_time=500):

    # http://research.cs.wisc.edu/htcondor/manual/v7.8/2_6Managing_Job.html#sec:job-prio

    ids_split = split_ids(ids, n=n_at_a_time)
    for ids_sub in ids_split:
        procargs = ['condor_prio', '-p', str(priority)] + ids_sub
        try_executing_until_succeed(procargs)

##__________________________________________________________________||
def split_ids(ids, n=500):
    # e.g.,
    # ids = [3158174', '3158175', '3158176', '3158177', '3158178']
    # n = 2
    # return [[3158174', '3158175'], ['3158176', '3158177'], ['3158178']]
    return [ids[i:(i + n)] for i in range(0, len(ids), n)]

##__________________________________________________________________||
