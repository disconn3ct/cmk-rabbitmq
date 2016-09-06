#!/usr/bin/python
#
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 3.  This test is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
# This configures the queue size/consumers limits in WATO.
#
group = "Applications, Processes & Services"

# def register_check_parameters(subgroup, checkgroup, title, valuespec, itemspec, matchtype, has_inventory=True, register_static_check=True):
# 
register_check_parameters(
    group,
    "rabbitmq_queues",
    _("RabbitMQ Queue Sizes"),
    Dictionary(
        elements = [
            ("size",
	     Tuple(
               title = _("Levels for the queue length"),
               help = _("Set the maximum and minimum length for the queue size"),
	       elements = [
                   Integer(title="Warning at a size of", minvalue=0),
                   Integer(title="Critical at a size of", minvalue=0),
               ]
            )),
            ("consumerCount",
            Tuple(
               title = _("Levels for the consumer count"),
               help = _("Consumer Count is the size of connected consumers to a queue"),
               elements = [
                  Integer(title="Warning less then"),
                  Integer(title="Critical less then"),
               ]
            )),
        ]
    ),
    TextAscii( title=_("Queue Name"),
    help=_("The name of the queue as listed in the queue manager")),
    "first",
)
