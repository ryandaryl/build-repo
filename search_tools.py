
from bs4 import BeautifulSoup
import nltk
from difflib import SequenceMatcher
from itertools import product
import requests, json, re, threading
from collections import namedtuple


def sentences_containing(html, word_array):

  def remove_tables(string_list):
    string_dict_list = []
    for i in string_list:
      string_dict_list.append({
        'text': i,
        'count': i.count(' ')
      })
    output_string_list = []
    for i, string_dict in enumerate(string_dict_list):
      window_length = 4
      moving_sum = sum([int(string_dict_list[j]['count'] > 2) for j in range(
                       max(i - window_length, 0),
                       min(i + window_length, len(string_dict_list)))])
      if moving_sum > window_length or string_dict['text'].count(' ') > 4:
        output_string_list.append(string_dict['text'])
    return output_string_list

  def fix_joined_sentences(input_string):
    word_list = input_string.split(' ')
    output_word_list = []
    for word in word_list:
      output_word_list.append(word.replace('.', '. ')
        if word.count('.') == 1
        and not all([i.isdigit() for i in (re.findall('(.)\.(.)', word) + [''])[-1]])
        else word)
    return ' '.join(output_word_list)

  if 'Ros Spence (Labor) since 2014.' in html:
    print('It is here.')
  word_list = sum([i['word_list'] for i in word_array], [])
  filtered_html = ''
  part_length = 1000
  padding_length = 200
  for i in range(0, len(html), part_length):
    slice_start = max(0, i - padding_length)
    slice_end = i + part_length + padding_length
    html_part = html[slice_start:slice_end]
    if all([word in html_part for word in word_list]):
      filtered_html += html_part
  html = filtered_html
  tags = BeautifulSoup(html, "html.parser").findAll()
  for tag in tags:
    tag_text = tag.text
    if not tag_text.split():
      continue
    if word_array[0]['word_list'][0] not in tag_text:
      continue
    if not all([all([j in tag_text for j in i['word_list']]) for i in word_array]): continue
    html = html.replace(str(tag), tag_text)
  sentences = []
  string_list = BeautifulSoup(html, "html.parser").strings
  string_list = [i.strip() for i in string_list if i.strip()]
  #string_list = remove_tables(string_list)
  for tag_string in string_list:
    if 'Ros Spence (Labor) since 2014.' in tag_string:
      print('Still here 4.')
    if not all([complex_string_search(tag_string, i) for i in word_array]): continue
    for i in ['\\n', '\\r', '\\t', '\n', '\r', '\t']:
      tag_string = tag_string.replace(i, ' ')
    tag_string = BeautifulSoup(tag_string, "html.parser").text
    for sentence in nltk.sent_tokenize(fix_joined_sentences(tag_string)):
      if set(sentence).intersection(set('@{}[]<>')):
        continue
      if not all([complex_string_search(sentence, i) for i in word_array]): continue
      if any([SequenceMatcher(None, i, sentence).ratio() > 0.95 for i in sentences]):
        continue
      sentences.append(sentence.strip())
  return sentences

def complex_string_search(input_string, search_config_dict):

  def filter_word_location_list(word_location_list, input_string, criteria_function):
    output_location_list = []
    for location_tuple in word_location_list:
      match_start = min([i.start for i in location_tuple])
      match_end = max([i.end for i in location_tuple])
      match_string = input_string[match_start:match_end]
      match_dict = {k: v for (k, v) in enumerate(match_string)}
      for (start, end) in [(i.start - match_start, i.end - match_start) for i in location_tuple]:
        for i in range(start, end):
          del match_dict[i]
      intervening_string = ''.join([i[1] for i in sorted(match_dict.items())])
      words = [i.strip() for i in intervening_string.split(' ') if i.strip()]
      if criteria_function(words):
        output_location_list.append(location_tuple)
    return output_location_list

  if len(input_string) > 2000:
    return []
  StringMatch = namedtuple('StringMatch', 'word start end')
  result_set = set()
  search_result_list = [[StringMatch(word, m.start(), m.end()) for m in
                         re.finditer(word, input_string)] for word in search_config_dict['word_list']]
  word_location_list = [i for i in product(*search_result_list) if [j.start for j in i] == sorted([j.start for j in i])]
  result_set.update(word_location_list)
  for criteria_name, criteria_args in search_config_dict['intervening_word_criteria'].items():
    criteria_function_dict = {
      'first_letter': lambda words: all([getattr(i[0], criteria_args)() for i in words]),
      'word_count_less_than': lambda words: len(words) < criteria_args
    }
    criteria_function = criteria_function_dict[criteria_name]
    result_set = result_set.intersection(set(filter_word_location_list(word_location_list, input_string, 

criteria_function)))
  return [tuple([dict(j._asdict()) for j in i]) for i in result_set]

def sentences_from_html(html, word_array):
  sentences = sentences_containing(html, word_array)
  output_list = []
  for sentence in sentences:
    word_index_list = [complex_string_search(sentence, i) for i in word_array]
    if not all(word_index_list):
      continue
    output_list.append({
      'search_data': word_array,
      'sentence': sentence,
      'word_index': word_index_list
    })
  return output_list


def run_with_timeout(func, max_time, default, args=()):

  def func_to_object(func, args):
    output_object['output'] = func(*args)

  output_object = {'output': default}
  t = threading.Thread(target=func_to_object, args=(func, args))
  t.daemon = True
  t.start()
  t.join(timeout=max_time)
  return output_object['output']


def sentences_from_search(word_array):

  def search_iteration(word_array, start):
    print('Searching, start = {}'.format(start))
    word_list = sum([i['word_list'] for i in word_array], [])
    url = ('https://www.googleapis.com/customsearch/v1?key=AIzaSyCzKywS_TUR-ck8Gm'
         + '-jqzUp3mqxibu35JA&cx=015926535567777788353:dqnmnvwaina&q=' + '+'.join(word_list)
         + '&start=' + str(start))
    try:
      r = requests.get(url, timeout=(5, 10))
      response_object = json.loads(r.text)
    except ConnectionError:
      response_object = {}
    if 'items' in response_object:
      result_list = response_object['items']
    else:
      result_list = []
    output_list = []
    for result in result_list:
      def my_request():
        try: 
          return requests.get(result['link']).text
        except ConnectionError:
          return ''
      html = run_with_timeout(func=my_request, max_time=30, default='', args=())
      if not html:
        continue
      html = ''.join([i if ord(i) < 128 else ' ' for i in html])
      sentence_object_list = sentences_from_html(html, word_array)
      for sentence_object in sentence_object_list:
        if output_list and any([SequenceMatcher(None, i['sentence'],
                               sentence_object['sentence']).ratio() > 0.95 for i in output_list]):
          continue
        sentence_object['url'] = result['link']
        output_list.append(sentence_object)
    print('Got {} results.'.format(len(output_list)))
    return output_list

  result_list = []
  start = 1
  while len(result_list) < 10 and start < 100:
    yield search_iteration(word_array, start)
    start += 10
