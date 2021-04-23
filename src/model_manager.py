#!/usr/bin/env python3
#
# Mainly just a rewrite of 'intractive_conditional_samples.py'
# from the gpt-2 'src' directory.
import sys
import json
import os
import numpy as np
import tensorflow.compat.v1 as tf

from gpt_2.src import encoder, model, sample


class ModelManager:
    def __init__(self, modelDir: str, modelName: str, allowGpu: bool = False):
        self.modelName = modelName
        self.modelDir = os.path.expanduser(os.path.expandvars(modelDir))

        # Number of batches to run (we only need 1 sample)
        batchSize = 1

        # Float value controlling randomness (Lower is less random)
        temperature = 0.4

        # Integer value controlling diversity. Basically the number
        # of words that are considered during sample generation.
        # (0 means to have no limit, but 40 is a good value)
        topK = 40

        # The 'interactiveConditional_samples.py' script does not say
        # what this value does.
        topP = 0.9

        # Required (Tensorflow will complain if this is not here)
        tf.compat.v1.disable_eager_execution()

        # Load encoder, and hparams
        self.enc = encoder.get_encoder(modelName, modelDir)
        self.hparams = model.default_hparams()
        with open(os.path.join(modelDir, modelName, 'hparams.json')) as f:
            self.hparams.override_from_dict(json.load(f))
        seed = np.random.randint(0, 100000)

        # The default from the hparams file
        # seems good enough.
        # length = self.hparams.n_ctx // 2
        length = 60

        config = None
        if allowGpu:
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
        else:
            config = tf.ConfigProto(device_count={"GPU": 0})

        self.sess = tf.Session(config=config)

        # Create a placeholder sample for self.sess.run to use.
        self.context = tf.placeholder(tf.int32, [batchSize, None])
        # np.random.seed(seed)
        # tf.set_random_seed(seed)

        self.output = sample.sample_sequence(
            hparams=self.hparams,
            length=length,
            context=self.context,
            batch_size=batchSize,
            temperature=temperature,
            top_k=topK,
            top_p=topP,
        )

        # Load pre-trained model
        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(modelDir, modelName))

        with tf.get_default_graph().as_default():
            saver.restore(self.sess, ckpt)

    def __del__(self):
        self.sess.close()

    def getSampleFromText(self, inputStr: str):
        # Convert string to tokens
        contextTokens = self.enc.encode(inputStr)

        # Generate sample
        out = self.sess.run(self.output,
                            feed_dict={self.context:
                                       [contextTokens]})[:,
                                                         len(contextTokens):]

        # Convert output tokens to a string
        text = self.enc.decode(out[0])

        return text


if __name__ == "__main__":
    modelsDir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             "../gpt2-model")
    modelsName = "rpg_model"

    testManager = ModelManager(modelsDir, modelsName)

    sampleText = "You are Craig, a knight. You have a sword, and a set of steel armor.\n"
    sampleText += "You are on your way to kill the dragon who killed your parents. You approach a nearby town with a blacksmith.\n"

    while True:
        print("========================================")
        print(sampleText)

        inputStr = input("> ")
        sampleText += "> " + inputStr + "\n"
        aiText = testManager.getSampleFromText(sampleText)
        actionIndex = aiText.find("> ")

        sampleText += aiText[:actionIndex]
