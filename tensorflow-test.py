#!/usr/bin/env python3
import tensorflow as tf

if __name__ == "__main__":
    # Test code from tensorflow's github repo.
    print(tf.add(1, 2).numpy())
    hello = tf.constant('Hello, Tensorflow!')
    print(hello.numpy())
