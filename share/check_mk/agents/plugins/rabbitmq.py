#!/usr/bin/python
#
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 3.  This testis  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
#
# This automatically tracks RabbitMQ statistics, including queue sizes
# and status.
#
# See if something is listening on 15672. If so, it is probably rabbitmq
# Some of this detection code is copied from the CMK nginx plugin
#
import os, sys, urllib2, re, json, base64

config_dir = os.getenv("MK_CONFDIR", "/etc/check_mk")
config_file = config_dir + "/rabbitmq.cfg"

servers = None
timeout=30

if os.path.exists(config_file):
	execfile(config_file)

def try_detect_servers():
	pids    = []
	results = []
	for line in os.popen('netstat -tlnp 2>/dev/null').readlines():
		parts = line.split()
		# Skip lines with wrong format
		if len(parts) < 7 or '/' not in parts[6]:
			continue

		pid, proc = parts[6].split('/', 1)
		to_replace = re.compile('^.*/')
		proc = to_replace.sub('', proc)

		procs = [ 'beam.smp' ]
		# the pid/proc field length is limited to 19 chars. Thus in case of
		# long PIDs, the process names are stripped of by that length.
		# Workaround this problem here
		procs = [ p[:19 - len(pid) - 1] for p in procs ]

		# Skip unwanted processes
		if proc not in procs:
			continue

		# Add only the first found port of a single server process
		if pid in pids:
			continue
		pids.append(pid)

		address, port = parts[3].rsplit(':', 1)
		port = int(port)

		# Use localhost when listening globally
		if address == '0.0.0.0':
			address = '127.0.0.1'
		elif address == '::':
			address = '::1'

		results.append((address, port))

	return results

def query_rmq(url,user,password):
	try:
			# Try to fetch the status page for each server
			headers = {"Accept":"application/json"}
			try:
					if user:
							authheader = "Basic %s" % base64.encodestring('%s:%s' % (user, password))[:-1]
							headers.update({"Authorization" : authheader })
					request = urllib2.Request(url, headers=headers)
					fd = urllib2.urlopen(request, timeout=timeout)
					return fd.read()
			except urllib2.URLError, e:
					raise
	except urllib2.HTTPError, e:
		sys.stderr.write('HTTP-Error (%s:%d): %s %s\n' % (address, port, e.code, e))

	except Exception, e:
		sys.stderr.write('Exception (%s:%d): %s\n' % (address, port, e))


if servers is None:
		servers = try_detect_servers()

if not servers:
	sys.exit(0)

for server in servers:
	if isinstance(server, tuple):
		address, port = server
		page = 'api/overview'
	else:
		address = server['address']
		port = server['port']
		user = server['user']
		password = server['password']
		page = server.get('page', 'api/overview')

	url = 'http://%s:%s/%s' % (address, port, page)

	# Now that we have a pile of JSON, lets break it up
	status=json.loads(query_rmq(url,user,password))
	if status['cluster_name']:
		print "<<<rabbitmq_cluster>>>"
		print status['cluster_name']
	print "<<<rabbitmq_listeners>>>"
	for i in range(len(status['listeners'])):
		listen=status['listeners'][i]
		print "%s\t%s\t%s\t%s" % (listen['node'],listen['ip_address'],listen['protocol'],listen['port'])
	print "<<<rabbitmq_message_stats>>>"
	print json.dumps(status['message_stats'])
	print "<<<rabbitmq_object_totals>>>"
	print json.dumps(status['object_totals'])
	print "<<<rabbitmq_queue_totals>>>"
	print json.dumps(status['queue_totals'])

	# Get detailed queue info
	page='api/queues'
	url = 'http://%s:%s/%s' % (address, port, page)
	queues=json.loads(query_rmq(url,user,password))
	# Parse it out into tab-separated info:
	# name state consumers messages messages_ready
	print "<<<rabbitmq_queues>>>"
	for i in range(len(queues)):
		tqueue=queues[i]
		print "%s\t%s\t%s\t%s\t%s" % (tqueue['name'],tqueue['state'],tqueue['consumers'],tqueue['messages'],tqueue['messages_ready'])

