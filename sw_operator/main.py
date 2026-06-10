import logging
import kopf
import sw_operator.handlers.main  # Importing triggers decorator registration

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **kwargs):
    settings.posting.level = logging.WARNING  # only post warnings/errors back to K8s events
    settings.persistence.finalizer = 'platform.eswar.dev/kopf-finalizer'


if __name__ == '__main__':
    kopf.run()