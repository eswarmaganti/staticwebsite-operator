import logging
import kopf
import sw_operator.handlers.main  # Importing triggers decorator registration

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **kwargs):
    settings.posting.level = logging.WARNING  # only post warnings/errors back to K8s events


if __name__ == '__main__':
    kopf.run()