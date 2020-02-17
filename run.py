from eve import Eve
import logging
import logging.handlers

def log_every_get(resource, request, payload):
    # custom INFO-level message is sent to the log file
    app.logger.info('GET Processed')

app = Eve()
app.on_post_GET += log_every_get

if __name__ == '__main__':
    # enable logging to 'app.log' file
    handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=10240, backupCount=5)

    # set a custom log format, and add request
    # metadata to each log line
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
        'url: %(url)s, method:%(method)s'))

    # the default log level is set to WARNING, so
    # we have to explictly set the logging level
    # to INFO to get our custom message logged.
    app.logger.setLevel(logging.INFO)

    # append the handler to the default application logger
    app.logger.addHandler(handler)

    app.run()