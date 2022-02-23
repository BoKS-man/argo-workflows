import argparse
from utils import check_model_size, Logger, process_model, save_result, load_weights
from model_mock import ModelMock

model_size_factor = 7
model_tensor_modificator = 1

def run(args):
    logger = Logger(model_size_factor, model_tensor_modificator)
    model = ModelMock(model_size_factor, model_tensor_modificator)
    if args.weights_path is not None:
        load_weights(model, args.weights_path)
    logger.log(f'The mock model is initialized (Size: {model_size_factor}, Add: {model_tensor_modificator}). Weights size is {check_model_size(model)} Mb')
    try:
        result = process_model(model, args.input_path, logger)
        logger.log(f'Resulted tensor mean is {result.mean()}')
    except Exception as e:
        logger.log(f'Model processing failure: {e}')
        raise e
    save_result(result, args.output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default='/input.pt')
    parser.add_argument('--output_path', type=str, default='/output.pt')
    parser.add_argument('--weights_path', type=str, default=None)
    args = parser.parse_args()
    run(args)