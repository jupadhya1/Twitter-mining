import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN



tf.flags.DEFINE_string("pos_file", None, "File containing positive examples")
tf.flags.DEFINE_string("neg_file", None, "File containing negative examples")
tf.flags.DEFINE_string("vocab_file", None, "Path to vocabulary file")
tf.flags.DEFINE_string("checkpoint_dir", None, "Checkpoint directory from training run")


tf.flags.DEFINE_integer("sequence_length", 200, 
    "The length of a sequence of words (default: 200)")
tf.flags.DEFINE_integer("batch_size", 128, "Batch size (default: 128)")


tf.flags.DEFINE_boolean("allow_soft_placement", True, 
    "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, 
    "Log placement of ops on devices")


FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")

if (not FLAGS.pos_file or not FLAGS.neg_file or not FLAGS.vocab_file 
    or not FLAGS.checkpoint_dir):
    print("--pos_file, --neg_file, --vocab_file and "
        "--checkpoint_dir must be specified")
    sys.exit(1)


print("Loading data...")
x_test, y_test, word2id, id2word = data_helpers.load_data(FLAGS.vocab_file, 
    FLAGS.pos_file, FLAGS.neg_file, FLAGS.sequence_length, 1000)
y_test = np.argmax(y_test, axis=1)
print("Vocabulary size: {:d}".format(len(word2id)))
print("Test set size {:d}".format(len(y_test)))

print("\nEvaluating...\n")



checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = (graph.get_operation_by_name("dropout_keep_prob").
            outputs[0])

        # Tensors  to evaluate
        predictions = (graph.get_operation_by_name("output/predictions").
            outputs[0])

       
        batches = data_helpers.batch_iter(x_test, FLAGS.batch_size, 1, 
            shuffle=False)

        
        all_predictions = np.array([])

        for x_test_batch in batches:
            batch_predictions = sess.run(predictions, {input_x: x_test_batch, 
                dropout_keep_prob: 1.0})
            all_predictions = np.concatenate([all_predictions, 
                batch_predictions])

correct_predictions = float(sum(all_predictions == y_test))
print("Total number of test examples: {}".format(len(y_test)))
print("Accuracy: {:g}".format(correct_predictions/len(y_test)))
