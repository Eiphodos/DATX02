import sys
sys.path.append("/home/musik/DATX02/tensor-v2/")
import LRModel
sys.path.append("/home/musik/DATX02/scripts/")
import training_data

# Linear regression checkpoint paths
LR_LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/linreg/loud"
LR_TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/linreg/tempo"
LR_MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/linreg/mode"

def main():
    # Linear regression output types
    lr_outputloud = Bucketizer.BucketType.LOUDNESS
    lr_outputmode = Bucketizer.BucketType.MODE
    lr_outputtempo = Bucketizer.BucketType.TEMPO

    # Linear regression estimators
    LoudLinReg = LRModel.LRModel(LR_LOUD_CKPT_PATH, lr_outputloud)
    ModeLinReg = LRModel.LRModel(LR_MODE_CKPT_PATH, lr_outputmode)
    TempoLinReg = LRModel.LRModel(LR_TEMPO_CKPT_PATH, lr_outputtempo)

    trainfeatures, tempolabels, modelabels, loudlabels = training_data.connect_and_get_data()

    LoudDNN.train(features=trainfeatures, labels=loudlabels)
    ModeDNN.train(features=trainfeatures, labels=modelabels)
    TempoDNN.train(features=trainfeatures, labels=tempolabels)

# If we run module as a script, run main
if __name__ == '__main__':
    main()