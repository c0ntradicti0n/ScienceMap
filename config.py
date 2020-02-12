htmls = "./pdfs/"
recursive = True
max_len = 200
max_len_amp = 20000

log_files = {
    "ccapp": "./log.log",
    "cc": "../CorpusCook/log.log",
    "dist": "../Distinctiopus/log.log"
}

paper_reader = "paper_reader.py"

cc_corpus_collection_path = "../CorpusCook/manually_annotated/"
cc_corpus_working_path = "../CorpusCook/server/corpus/"
dist_corpus_path = "../Distinctiopus4/manual_corpus/"

mixer_path = "../CorpusCook/manually_annotated/mix_corpus_from_manual_files.py"
mixer_working_dir =  "../CorpusCook/"
corpuscook_venv = "../CorpusCook/venv/bin/activate"

science_map_corpus_path="../ScienceMap/manual_corpus/"
science_map_working_dir="../ScienceMap/"
science_map="../ScienceMap/science_map.py"
science_map_venv="../ScienceMap/venv/bin/activate"
science_map_csv="../ScienceMap/manual_corpus/relations.csv"

ampligraph_working_dir="../KnowledgeScience/"
ampligraph_venv="../KnowledgeScience/venv/bin/activate"
ampligraph="../KnowledgeScience/csv_ampligraph.py"
ampligraph_coords="CONSTRASTSUBJECT"

train_venv_python = "../Distinctiopus4/venv/bin/activate"
train_path= "../Distinctiopus4"
train_script= "../Distinctiopus4/do/train_multi_corpus.py"
train_log = "../train.log"
allennlp_config = "../Distinctiopus4/experiment_configs/elmo_lstm3_feedforward4_crf_straight_fitter.config"

dist_model_path_first = "../Distinctiopus4/output/first_./experiment_configs/{config}/model.tar.gz".format(config=allennlp_config)
cc_model_path_first   = "../CorpusCook/server/models/model_first.tar.gz"
dist_model_path_over  = "../Distinctiopus4/output/over_./experiment_configs/{config}/model.tar.gz".format(config=allennlp_config)
cc_model_path_over    = "../CorpusCook/server/models/model_over.tar.gz"

vidgeo_dir = '../apache-tomcat-9.0.30/webapps/corpuscow/'
all_coordinates="../../KnowledgeScience/knowledge_graph_coords/knowledge_graph_3d_choords.csv"
ke_path=  "../../KnowledgeScience/knowledge_graph_coords/tsne_clusters_mean_points.csv"
ke_colors="../../KnowledgeScience/knowledge_graph_coords/tsne_clusters_mean_points.csv"
hal = '"../../../hal/target/hal-1-jar-with-dependencies.jar"'
apache_dir = "."

