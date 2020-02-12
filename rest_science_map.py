import json
import os
import subprocess

from flask import request
from flask import Flask

import config

app = Flask(__name__)



@app.route("/science_coords", methods=['GET'])
def science_coords():
    ''' give file '''
    if request.method == 'GET':
        cmd = f"""export PYTHONPATH=$PYTHONPATH:{config.ampligraph_working_dir}; . {config.ampligraph_venv} && python {config.ampligraph} {config.science_map_csv}"""

        logging.info("mapping graph to coordinates " + cmd)

        subprocess.Popen(cmd, cwd=config.ampligraph_working_dir, shell=True, preexec_fn=os.setsid)
    return []


@app.route("/science_video", methods=['GET'])
def science_video():
    ''' give file '''
    if request.method == 'GET':
        cmd = "ls; xvfb-run -a java -jar {hal} -all {all_coordinates} -c {colors} -p {path} -d 13 -m 100000 -v 2.7354  -h blub".format(
            all_coordinates=config.all_coordinates,
            colors=config.ke_colors,
            path=config.ke_path,
            hal=config.hal
        )
        logging.info(f"making video of journey {cmd} in dir {config.video_dir}")
        p = subprocess.Popen(cmd, cwd=config.video_dir, shell=True)
        (output, err) = p.communicate()

        cmd = "ffmpeg -y -i record.mp4 -acodec libfaac -ab 96k -vcodec libx264 -crf 20 -vf scale=1440:1080 record_compressed.mp4  ;" + \
              f"cp ./record_compressed.mp4 {config.apache_dir}"
        logging.info("compressing video\n" + cmd)
        subprocess.Popen(cmd, cwd=config.video_dir, shell=True)
        logging.info("video finished")
    return []



@app.route("/contrinference", methods=['GET'])
def counter_inference():
    ''' give file '''
    if request.method == 'GET':
        which = request.args['which']
        logging.info("give log " + which)
        path = "../CorpusCook/manually_annotated/"
        import contrinference
        contrinference.main(path)
    else:
        logging.error("not a post request")
    return ""


@app.route("/science_map", methods=['GET'])
def science_map():
    ''' give file '''
    if request.method == 'GET':
        which = request.args['which']
        logging.info("give log " + which)
        rets = []

        cmd = f"cp {config.cc_corpus_collection_path}/*.conll3 {config.science_map_corpus_path}"
        logging.debug(str(os.system(cmd)))

        cmd = f"""export PYTHONPATH=$PYTHONPATH:{config.science_map_working_dir} &&  
              bash {config.science_map_venv} &&
              python {config.science_map} {config.science_map_corpus_path}"""

        logging.info("doing sciencemapping" + cmd)
        subprocess.Popen(cmd, cwd=config.science_map_working_dir, shell=True, preexec_fn=os.setsid)

        return json.dumps(rets)
    return []

if __name__ == '__main__':
    import logging, logging.config, yaml

    logfile = logging.getLogger('file')
    logconsole = logging.getLogger('console')
    logfile.debug("Debug FILE")
    logconsole.debug("Debug CONSOLE")
    app.url_map.strict_slashes = False

    app.run(port=5556, debug=True)



