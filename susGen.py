# Generate exciting but semantically unpredictable (!!) sentences. 
from nltk import tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import re
import random
import inflect
# import treetaggerwrapper # multilingual tokenizer
from bs4 import BeautifulSoup
# os.popen("/Applications/anaconda/bin/python3.6 -m pip install --user wikipedia") # uncomment if machine needs wikipedia
import wikipedia

# modules
# getting source text and pos tagging (text processing)
# making sentence

engine = inflect.engine()
wordnet_lemmatizer = WordNetLemmatizer()

class TextProcessor(object):
	def __init__(self):
		# wiki_page = "Shark"
		# wikipedia.set_lang("simple")

		wiki_page = "Holland" # search term
		print("Extracting sentences from: ", wiki_page)
		# wikipedia.set_lang('en')  # to mess about with other languages
		# page_titles = wikipedia.search(wiki_page) # returns list of page titiles 
		# wiki_pages = []
		# for title in page_titles:
		# 	try:
		# 		wikipedia.page(title)
		# 		wiki_pages.append(wikipedia.page(title))
		# 	except wikipedia.exceptions.DisambiguationError:
		# 		continue

		# self.wiki_sum_list = [ wiki.content for wiki in wiki_pages]
		# wiki_content = ""
		# for content in self.wiki_sum_list:
		# 	wiki_content += content
		wiki = wikipedia.page(wiki_page)
		self.wiki_sum = wiki.content
		# self.wiki_sum = wiki_content

		# soup = BeautifulSoup(open('/Users/YuanyuanTian/Downloads/facebook-ganclarke/messages/200.html'), 'html.parser')
		# fb_msg = [ line.get_text() for line in list(soup.find_all('p')) if line.get_text() not in "George Aaron Nelson Clarke"]

		# self.words = [word for line in fb_msg for word in tokenize.word_tokenize(line)]
		self.words = tokenize.word_tokenize(self.wiki_sum)
		pos_tagged = pos_tag(self.words)  # returns list with each element as a two element tuple.

		self.word_pos_dict = {}
		self.get_word_pos_dict(pos_tagged) # fills up word pos dictionary

		self.pos_list = []  # creates a dictionary containing all possible pos tags from nltk
		self.get_pos_list()

		self.pos_words_dict = {}
		self.get_pos_words_dict(self.word_pos_dict)
		self.remove_bad_tokens()


	def get_word_pos_dict(self, pos_tagged):
		for tuple in pos_tagged:
			if tuple[0] != tuple[1]:
				self.word_pos_dict[tuple[0]] = tuple[1]

	def get_pos_list(self):
		with open('nltk_pos_tags.txt', 'r') as f:
			for line in f:
				self.pos_list.append(line[0:-1])  # removes that pesky new lin \n

	def get_pos_words_dict(self, word_pos_dict):
		for pos in self.pos_list:
			self.pos_words_dict[pos] = []
			for k, v in word_pos_dict.items():  # k is word and v is pos tag from nltk
				if v == pos:
					self.pos_words_dict[v].append(k)  # adds word to value list, eg. NNP : ['Japan', 'China', ... ]

	def remove_bad_tokens(self):
		pattern = re.compile(r'[^\s\w]') # deletes addition of ']' etc into wod options.
		for key in self.pos_words_dict:
			for idx, word in enumerate(self.pos_words_dict[key]):
				match = re.match(pattern, word)
				if match:
					del self.pos_words_dict[key][idx]

class Sentence(TextProcessor):
	def __init__(self):
		super(Sentence, self).__init__()

		self.posp_list = ['DT', 'NN', 'JJ', 'VBZ', 'RB']  # pos tags wanted for setnence


		self.dt_rand_idx = 0
		self.dt_rand_idx2 = 0
		self.nn_rand_idx = 0
		self.nn_rand_idx2 = 0
		self.vbz_rand_idx = 0

		self.set_rand_idx(self.posp_list) # updates the above random indexes

		self.noun_nn = ""
		self.verb = ""
		self.noun_nn2 = ""

		self.optional_adj1 = ""
		self.optional_adj2 = ""

		self.det_tuple = self.set_plurality(self.pos_words_dict, self.dt_rand_idx, self.nn_rand_idx, self.vbz_rand_idx, self.dt_rand_idx2, self.nn_rand_idx2)
		self.det_tuple2 = self.set_a_an(self.det_tuple)

		self.cap_word = self.det_tuple2[0]
		self.dt2 = self.det_tuple2[1]

	def set_rand_idx(self, posp_list): # sets a random index for the list of words for each pos tag
		self.dt_len = len(self.pos_words_dict[posp_list[0]])
		self.nn_len = len(self.pos_words_dict[posp_list[1]])
		self.vbz_len = len(self.pos_words_dict[posp_list[3]])

		# assigns a random int up to maximum length of pos list of words
		# a second one has been added in case where two nouns may be used in a sentence, or two determiners
		self.dt_rand_idx = random.randrange(0, self.dt_len)
		self.dt_rand_idx2 = random.randrange(0, self.dt_len)
		self.nn_rand_idx = random.randrange(0, self.nn_len)
		self.nn_rand_idx2 = random.randrange(0, self.nn_len)
		self.vbz_rand_idx = random.randrange(0, self.vbz_len)


	def opt_adj(self, posp_list, int):
		"""
		:param int:  sets the bar for the random number generator. higher number means less chance it will be used
		:return: depending on random generator an adjective is generatored or not
		"""
		jj_len = len(self.pos_words_dict[posp_list[2]])
		jj_rand_idx = random.randrange(0, jj_len)

		opt_adj = random.randrange(0, int)
		if opt_adj == 0:
			return " " + self.pos_words_dict['JJ'][jj_rand_idx] + " "
		else:
			return " "

	def opt_adv(self, posp_list, int):
		rb_len = len(self.pos_words_dict[posp_list[4]])
		print(rb_len)
		rb_rand_idx = random.randrange(0, rb_len) # sets the random index for adverb

		opt_adv = random.randrange(0, int)
		if opt_adv == 0: # only outputs an adverb if random num == 0
			return " " + self.pos_words_dict['RB'][rb_rand_idx] + " "
		else:
			return " "

	def set_plurality(self, pos_words_dict, dt_rand_idx,
					  nn_rand_idx, vbz_rand_idx, dt_rand_idx2,
					  nn_rand_idx2):
		"""
		This function sets the nouns and verbs to reflect plurality if the chosen determiner is plural
		:param pos_words_dict: pos : ['word1', 'word2' ... 'wordN'] a dictionary containing list of words related to that pos tag, eg. NN
		:param dt_rand_idx: sets the determiner index
		:param nn_rand_idx: sets the noun index
		:param vbz_rand_idx: sets the verb index
		:param dt_rand_idx2: sets the second determiner index
		:param nn_rand_idx2:  sets the second noun index
		:return: updates __init__ values for sentence's nouns and verb. Marked for plurality.
		"""
		first_word = pos_words_dict['DT'][dt_rand_idx]
		cap_word = first_word[0].upper() + first_word[1:]  # capitalises first determiner

		plural_dt = ['those', 'these', 'all', 'some', 'both', 'Those', 'These', 'All', 'Some', 'Both']
		noun_nn = pos_words_dict['NN'][nn_rand_idx]  #  sets noun
		verbal_3rd = pos_words_dict['VBZ'][vbz_rand_idx]  # sets verb
		verbal_all = wordnet_lemmatizer.lemmatize(verbal_3rd, 'v')  # makes non3P version of verbal_3rd

		# fixes verb agreement
		if cap_word in plural_dt:  # checks to see if first determiner is plural
			self.noun_nn = engine.plural(noun_nn)  # set noun to plural form
			self.verb = verbal_all  # set verb to non3P form
		else:
			self.noun_nn = noun_nn
			self.verb = verbal_3rd

		dt2 = pos_words_dict['DT'][dt_rand_idx2].lower()  # sets sentence second determiner
		noun_nn2 = pos_words_dict['NN'][nn_rand_idx2]  # sets sentence second noun

		if dt2 in plural_dt:
			self.noun_nn2 = engine.plural(noun_nn2)  # sets noun to plural if det is plural
		else:
			self.noun_nn2 = noun_nn2

		return cap_word, dt2

	def set_a_an(self, dets):
		cap_word = dets[0]
		dt2 = dets[1]

		a_an_dt = ['a', 'an', 'A', 'An']

		self.optional_adj1 = self.opt_adj(self.posp_list, 1) #  generates a random adjective or no adjective.
		optional_adj1 = self.optional_adj1
		# fixes a/an issue
		if cap_word in a_an_dt:  # if first determiner in sentence is an indefinite article
			if not optional_adj1 == "":  # if adjective 1 is set
				cap_words = engine.a(optional_adj1)  # set the indefinite article to be a or an depending on the adjective
				word_len = len(optional_adj1)
			else:
				cap_words = engine.a(self.noun_nn)  # else do same but for the noun, in lieu of adjective
				word_len = len(self.noun_nn)

			cap_word = cap_words[0:-word_len]  # cap word has a noun now, so this removes that noun and any annoying spaces
			# sets first determiner article as upper case: A or An
			if cap_word == "a" or cap_word == " a":
				if cap_word[1:] == "an": # bug with "an" slipping by
					cap_word = "an"
				elif len(cap_word) > 1:
					cap_word = cap_word[1]
				cap_word = cap_word.upper()
			else:
				cap_word = cap_word[1].upper() + cap_word[2]

		self.optional_adj2 = self.opt_adj(self.posp_list, 1)
		optional_adj2 = self.optional_adj2

		if dt2 in a_an_dt:
			if not optional_adj2 == "":
				dt2 = engine.a(optional_adj2)
				word_len = len(optional_adj2)
				dt2 = dt2[1:-word_len]
			else:
				dt2 = engine.a(self.noun_nn2)
				word_len = len(self.noun_nn2)
				dt2 = dt2[0:-word_len]

		return cap_word, dt2

	def random_sentence(self):
		# det (adj)noun verb(adv) det (adj)noun - the basic structure for a sentence with optionals in ()
		#    DT  + (JJ)NN + VBZ(RB) + DT + (JJ)NN - # convert to pos tags
		# sus_sentence = self.cap_word + self.optional_adj1.lower() + self.noun_nn.lower() + " " + self.verb.lower() + self.opt_adv(self.pos_list, 8).lower() + self.dt2.lower() + self.optional_adj2.lower() + self.noun_nn2.lower() + "."
		sus_sentence = self.cap_word + self.optional_adj1.lower() + self.noun_nn.lower() + " " + self.verb.lower() +" "+ self.dt2.lower() + self.optional_adj2.lower() + self.noun_nn2.lower() + "."
		return sus_sentence

	def write2file(self, sentences, iter_boi):
		"""
			This writes 20 randomly generated sentences.
			:param: random_sentence: generated from calling the sentence generator function
			:return: outputs to a text file called 'sus_sentence'
		"""

		print("Writing to file... \n ")
		with open('sus_sentences_classes.txt', 'a') as f:
			sus_sentence = str(iter_boi) + " " + sentences + "\n"
			print(sus_sentence)
			f.write(sus_sentence)
if __name__ == '__main__':
	random_sentence = Sentence()
	ranglen = int(input("How many sentences would you like to generate? "))
	for i in range(ranglen):
		random_sentence = Sentence()
		random_sentence.write2file(random_sentence.random_sentence(), i+1)
