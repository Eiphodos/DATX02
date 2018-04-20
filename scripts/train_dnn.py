import sys
sys.path.append("/home/musik/DATX02/server/userdata/")
import Bucketizer
sys.path.append("/home/musik/DATX02/tensor-v2/")
import DNNModel
sys.path.append("/home/musik/DATX02/scripts/")
import training_data

# DNN checkpoint paths
DNN_LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/loud"
DNN_TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/tempo"
DNN_MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/mode"

def main():
    # DNN output types
    dnn_outputloud = Bucketizer.BucketType.LOUDNESS
    dnn_outputmode = Bucketizer.BucketType.MODE
    dnn_outputtempo = Bucketizer.BucketType.TEMPO

    # DNN estimators
    LoudDNN = DNNModel.DNNModel(DNN_LOUD_CKPT_PATH, dnn_outputloud)
    ModeDNN = DNNModel.DNNModel(DNN_MODE_CKPT_PATH, dnn_outputmode)
    TempoDNN = DNNModel.DNNModel(DNN_TEMPO_CKPT_PATH, dnn_outputtempo)

    trainfeatures, tempolabels, modelabels, loudlabels = training_data.connect_and_get_data()

    LoudDNN.train(features=trainfeatures, labels=loudlabels)
    ModeDNN.train(features=trainfeatures, labels=modelabels)
    TempoDNN.train(features=trainfeatures, labels=tempolabels)

# If we run module as a script, run main
if __name__ == '__main__':
    main()