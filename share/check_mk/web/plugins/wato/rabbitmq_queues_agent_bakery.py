group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:rabbitmq_queues",
    Alternative(
        title = _("RabbitMQ Queues"),
        help = _("This will deploy the agent plugin <tt>rabbitmq.py</tt> on linux systems "
                 "for monitoring several aspects of RabbitMQ."),
        style = "dropdown",
        elements = [
            Dictionary(
                title = _("Deploy the RabbitMQ plugin"),
                elements = [
                    ("credentials", Tuple(
                        title = _("Credentials to access RabbitMQ"),
                        elements = [
                            TextAscii(
                                title = _("User ID"),
                                default_value = "monitoring",
                            ),
                            Password(
                                title = _("Password")
                            ),
                        ]
                    )),
                    ("port", Integer(
                                title=_("Port"),
                                minvalue=1,
                                maxvalue=65535,
                                default_value = 15672)),
                    ("interval", Age(
                        title = _("Run asynchronously"),
                        label = _("Interval for collecting data"),
                        default_value = 300
                    )),
                ],
            ),
            FixedValue(None, title = _("Do not deploy the RabbitMQ plugin"), totext = _("(disabled)") ),
        ]
    )
)
