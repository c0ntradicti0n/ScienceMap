import json

from flask import request
from flask import Flask
app = Flask(__name__)



@app.route("/science_map", methods=['GET'])
def migrate_corpus():
    ''' give file '''
    if request.method == 'GET':
        which = request.args['which']
        logging.info("give log " + which)
        path = "../CorpusCook/manually_annotated/"
        import GUI
        GUI.main(path)
    else:
        logging.error("not a post request")
    return ""

if __name__ == '__main__':
    import logging, logging.config, yaml

    logfile = logging.getLogger('file')
    logconsole = logging.getLogger('console')
    logfile.debug("Debug FILE")
    logconsole.debug("Debug CONSOLE")
    app.url_map.strict_slashes = False

    app.run(port=5556, debug=True)



