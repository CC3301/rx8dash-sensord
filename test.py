import atexit
import datetime
import os
import signal
import sys
import time

from aggregator import SensorAggregator


class Daemon(object):
    """ Linux Daemon boilerplate. """
    def __init__(self, pid_file,
                 stdout='/var/log/daemon_example_out.log',
                 stderr='/var/log/daemon_example_err.log'):
        self.stdout = stdout
        self.stderr = stderr
        self.pid_file = pid_file
        self.aggregator = SensorAggregator()

    def del_pid(self):
        """ Delete the pid file. """
        os.remove(self.pid_file)

    def daemonize(self):
        """ There shined a shiny daemon, In the middle, Of the road... """
        # fork 1 to spin off the child that will spawn the daemon.
        if os.fork():
            sys.exit()

        # This is the child.
        # 1. cd to root for a guaranteed working dir.
        # 2. clear the session id to clear the controlling TTY.
        # 3. set the umask, so we have access to all files created by the daemon.
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # fork 2 ensures we can't get a controlling ttd.
        if os.fork():
            sys.exit()

        # This is a child that can't ever have a controlling TTY.
        # Now we shut down stdin and point stdout/stderr at log files.

        # stdin
        with open('/dev/null', 'r') as dev_null:
            os.dup2(dev_null.fileno(), sys.stdin.fileno())

        # stderr - do this before stdout so that errors about setting stdout write to the log file.
        #
        # Exceptions raised after this point will be written to the log file.
        sys.stderr.flush()
        with open(self.stderr, 'a+', 1) as stderr:
            os.dup2(stderr.fileno(), sys.stderr.fileno())

        # stdout
        #
        # Print statements after this step will not work. Use sys.stdout
        # instead.
        sys.stdout.flush()
        with open(self.stdout, 'a+', 1) as stdout:
            os.dup2(stdout.fileno(), sys.stdout.fileno())

        # Write pid file
        # Before file creation, make sure we'll delete the pid file on exit!
        atexit.register(self.del_pid)
        pid = str(os.getpid())
        with open(self.pid_file, 'w+') as pid_file:
            pid_file.write('{0}'.format(pid))

    def get_pid_by_file(self):
        """ Return the pid read from the pid file. """
        try:
            with open(self.pid_file, 'r') as pid_file:
                pid = int(pid_file.read().strip())
            return pid
        except IOError:
            return

    def start(self):
        """ Start the daemon. """
        print("Starting...")
        if self.get_pid_by_file():
            print('PID file {0} exists. Is the daemon already running?'.format(self.pid_file))
            sys.exit(1)

        self.daemonize()
        self.aggregator.start()
        self.run()

    def stop(self):
        """ Stop the daemon. """
        print("Stopping...")
        pid = self.get_pid_by_file()
        if not pid:
            print("PID file {0} doesn't exist. Is the daemon not running?".format(self.pid_file))
            return

        # Time to kill.
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            if 'No such process' in err.strerror and os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            else:
                print(err)
                sys.exit(1)

    def restart(self):
        """ Restart the daemon. """
        self.stop()
        self.start()

    def run(self):
        """ The main loop of the daemon. """
        while 1:
            with open(self.stdout, 'w') as stdout:
                stdout.write(str(self.aggregator.fetch()))
            time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {0} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)

    daemon = Daemon('/tmp/daemon_example.pid')
    if 'start' == sys.argv[1]:
        daemon.start()
    elif 'stop' == sys.argv[1]:
        daemon.stop()
    elif 'restart' == sys.argv[1]:
        daemon.restart()
    else:
        print("Unknown command '{0}'".format(sys.argv[1]))
        sys.exit(2)
