
from search_tools import sentences_from_search
import stanfordnlp
import os
import json
import urllib
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from celery.signals import worker_process_init
broker = os.environ['REDIS_URL']
backend = os.environ['REDIS_URL']
name = os.environ.get('CELERY_NAME', 'default_name')

nlp = None
celery = Celery(name, broker=broker,
                backend=backend)

def remove_parent(input_dict):
  input_dict.pop('_parent_token', None)
  return input_dict

def word_dict_from_sentence(sentence_string, nlp):

  def add_location_to_word_dict(word_dict, sentence_string):
    output_dict = {}
    location = 0
    for id, word_data in sorted(word_dict.items(), key=lambda x: x[0]):
      output_dict[id] = word_data
      new_index = sentence_string.find(word_data['_text'], location)
      if new_index <= -1:
        continue
      location = new_index
      output_dict[id]['start'] = location
      location += len(word_data['_text'])
      output_dict[id]['end'] = location
    return output_dict

  def correct_lemmas(word_dict):
    output_dict = word_dict.copy()
    for node_dict in output_dict.values():
      if all(i.isupper() for i in node_dict['_text'][:-1]) and node_dict['_text'][-1] == 's':

        node_dict['_lemma'] = node_dict['_text'].lower()[:-1]
    return output_dict

  filler = False
  sentences = nlp(sentence_string).sentences
  if len(sentences) > 1:
    test_sentences = nlp('The ' + sentence_string).sentences
    if len(test_sentences) == 1:
      sentences = test_sentences
      filler = True
  if len(sentences) > 1:
    sentences = nlp(sentence_string.replace('.', '')).sentences
  if len(sentences) != 1:
    return {}
  word_dict = {}
  for i in sentences[0].tokens:
    for j in i.words:
      word = remove_parent(j.__dict__)
      word['_index'] = int(word['_index'])
      if filler == True and word['_index'] == 1 and word['_text'] == 'The':
        continue
      word_dict[word['_index']] = word
  for (i, j, k) in sentences[0].dependencies:
    for m in [i, k]:
      word = remove_parent(m.__dict__)
      word['_index'] = int(word['_index'])
      if filler == True and word['_index'] == 1 and word['_text'] == 'The':
        continue
      word_dict[word['_index']] = word
  word_dict = correct_lemmas(word_dict)
  word_dict = add_location_to_word_dict(word_dict, sentence_string)
  return word_dict

@worker_process_init.connect()

def on_worker_init(**_):

    import nltk
    nltk.download('punkt')
    import stanfordnlp
    stanfordnlp.download('en', force=True)
    global nlp
    nlp = stanfordnlp.Pipeline(lang="en",use_gpu=False)

@celery.task(name='celery_worker.search', bind=True)
def search(self, data):
    data_json = json.loads(urllib.parse.unquote(data.get('data', '{}')))
    task_id = self.request.id
    output_list = []
    try:
      for sentence_object_list in sentences_from_search(data_json):
        for sentence_object in sentence_object_list:
          sentence_object['word_dict'] = word_dict_from_sentence(sentence_object['sentence'], nlp)
          output_list.append(sentence_object)
          self.update_state(state='PENDING', meta=output_list)
          if len(output_list) >= 10:
            return output_list
    except SoftTimeLimitExceeded:
      pass
    return output_list
