import tensorflow as tf

def argmax_2d(tensor):

  # input format: BxHxWxD
  assert rank(tensor) == 4

  # flatten the Tensor along the height and width axes
  flat_tensor = tf.reshape(tensor, (tf.shape(tensor)[0], -1, tf.shape(tensor)[3]))

  # argmax of the flat tensor
  argmax = tf.cast(tf.argmax(flat_tensor, axis=1), tf.int32)

  # convert indexes into 2D coordinates
  argmax_x = argmax // tf.shape(tensor)[2]
  argmax_y = argmax % tf.shape(tensor)[2]

  # stack and return 2D coordinates
  return tf.stack((argmax_x, argmax_y), axis=1)



def rank(tensor):

  # return the rank of a Tensor
  return len(tensor.get_shape())
