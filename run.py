import argparse

def run(args):
    with open(args.input, 'r') as f:
        digit = int(f.readline())
    print(f'received digit {digit}')

    digit += 1

    with open(args.output, 'w') as f:
        f.write(str(digit))

    print(f'sended digit {digit}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()
    run(args)