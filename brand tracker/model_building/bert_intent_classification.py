import os
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
"""
0 = all messages are logged (default behavior)
1 = INFO messages are not printed
2 = INFO and WARNING messages are not printed
3 = INFO, WARNING, and ERROR messages are not printed

To avoid the model taking up to much RAM, in the text training cycle on the model decrease the batch_size

"Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2"
- The warning states that your CPU does support AVX; No breaking issue.

"""

import tensorflow as tf
from tensorflow import keras
from bert.tokenization.bert_tokenization import FullTokenizer

def bert (text):
    model = tf.keras.models.load_model('saved_model/latest_bert_model')

    bert_model_name="uncased_L-12_H-768_A-12"
    bert_ckpt_dir = os.path.join("model/", bert_model_name)
    tokenizer = FullTokenizer(vocab_file=os.path.join(bert_ckpt_dir, "vocab.txt"))

    pred_tokens = map(tokenizer.tokenize, text)
    pred_tokens = map(lambda tok: ["[CLS]"] + tok + ["[SEP]"], pred_tokens)
    pred_token_ids = list(map(tokenizer.convert_tokens_to_ids, pred_tokens))

    # Stems from IntentDetectionData max_seq_len: 128
    max_seq_len = 128
    classes = ['Request', 'Opinion', 'Issue']

    pred_token_ids = map(lambda tids: tids +[0]*(max_seq_len-len(tids)),pred_token_ids)
    pred_token_ids = np.array(list(pred_token_ids))

    predictions = model.predict(pred_token_ids).argmax(axis=-1)
    intent = classes[predictions[0]]

    return intent