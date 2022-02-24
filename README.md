# Argo Workflows установка и примеры использования

## Установка и настройка

### Docker
``` bash
sudo apt-get update

sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"

sudo apt-get update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

### Установка и первичная настройка локального кластера Kubernetes

Были исследованы следующие инструменты для создания локального кластера: MiniCube и K3D. В качестве основного инструмента был выбран K3D в силу простоты работы и отсутствия проблем в условиях работы на виртуальной машины.

#### Создание кластера и установка инструменов управления 
используемые в коде переменные:
* NAMESPACE: Имя пространства имён в кластере K8s в котором будет располагаться экземпляр Argo Workflows
``` bash
wget -q -O - https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash

k3d cluster create <NAMESPACE>

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update

sudo apt -y install vim git curl wget kubelet kubeadm kubectl

sudo apt-mark hold kubelet kubeadm kubectl
```

#### Отключение SWAP
``` bash
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

sudo swapoff -a
```

### Argo Workflows
* NAMESPACE: Имя пространства имён в кластере K8s в котором располагается экземпляр Argo Workflows
``` bash
kubectl create ns <NAMESPACE>

kubectl apply -n <NAMESPACE> -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
```

#### предоставление админских прав для учётки, под которой будут выполняться пайплайны
используемые в коде переменные:
* MINIO_SECRET: Имя учётной записи
* EMAIL: Адрес электронной почты учётной записи
``` bash
kubectl create clusterrolebinding <MINIO_SECRET>-cluster-admin-binding --clusterrole=cluster-admin --user=<EMAIL>
```

### Argo CLI
``` bash
curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.3.0-rc6/argo-linux-amd64.gz

gunzip argo-linux-amd64.gz

chmod +x argo-linux-amd64

mv ./argo-linux-amd64 /usr/local/bin/argo
```

#### Проверка установки
``` bash
argo version
```
Пример результата:
``` bash
argo: v3.3.0-rc6
  BuildDate: 2022-02-21T20:24:30Z
  GitCommit: 79fc4a9bea8d76905d314ac41df7018b556a91d6
  GitTreeState: clean
  GitTag: v3.3.0-rc6
  GoVersion: go1.17.7
  Compiler: gc
  Platform: linux/amd64
```

### Nomebrew
``` bash
sudo apt update
sudo apt upgrade

sudo apt install build-essential curl file git

sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"
```

### Helm
``` bash
brew install helm

helm repo add minio https://helm.min.io/

helm repo update
```

### MinIO
используемые в коде переменные:
* MINIO_SECRET: Имя secret раздела в argo, содержащего информацию об учётных данных экземпляра MinIO
* NAMESPACE: Имя пространства имён в кластере K8s в котором располагается экземпляр Argo Workflows
``` bash
helm install <MINIO_SECRET> minio/minio --set service.type=LoadBalancer --set fullnameOverride=<NAME> --namespace=<NAMESPACE>
```


#### Получениеучётных данных
используемые в коде переменные:
* MINIO_SECRET: Имя secret раздела в argo, содержащего информацию об учётных данных экземпляра MinIO
* NAMESPACE: Имя пространства имён в кластере K8s в котором располагается экземпляр Argo Workflows
* URL: адрес и порт для доступа к экземпляру MinIO
* ACCESSKEY: ключ доступа
* SECRETKEY: секретный ключ
``` bash
kubectl get service <MINIO_SECRET> –namespace=<NAMESPACE>
```
Пример результата:
``` bash
NAME             TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
argo-artifacts   LoadBalancer   10.43.51.172   172.20.0.3    9000:32153/TCP   3d2h
```
URL = EXTERNAL-IP

``` bash
kubectl get secret <MINIO_SECRET> -o jsonpath='{.data.accesskey}' | base64 --decode
```
Пример результата:
``` bash
0Nd8v417Jr4j21z02qYs
```
ACCESSKEY = результат

``` bash
kubectl get secret <MINIO_SECRET> -o jsonpath='{.data.secretkey}' | base64 --decode
```
Пример результата:
``` bash
tcadXWDI3iP1ROfqCr4UCPjtKLFZ2matgMKapXzm
```
SECRETKEY = результат

### MinIO Client
используемые в коде переменные:
* URL: адрес и порт для доступа к экземпляру MinIO
* ACCESSKEY: ключ доступа
* SECRETKEY: секретный ключ
``` bash
brew install minio/stable/mc

mc alias set minio http://<URL> <ACCESSKEY> <SECRETKEY>
```

### Натсройка Argo для работы с MinIO
используемые в коде переменные:
* MINIO_SECRET: Имя secret раздела в argo, содержащего информацию об учётных данных экземпляра MinIO
* NAMESPACE: Имя пространства имён в кластере K8s в котором располагается экземпляр Argo Workflows
* URL: адрес и порт для доступа к экземпляру MinIO
* ACCESSKEY: ключ доступа
* SECRETKEY: секретный ключ
* BUCKET: имя bucket'а в MinIO

#### Создание bucket'а по-умолчанию в MinIO
``` bash
mc mb minio/<BUCKET>
```

#### Настройка конфигурации кластера K8s
``` bash
kubectl edit configmap workflow-controller-configmap -n <NAMESPACE>
```
в открывшемся файле изменяем раздел data следующим образом:
``` yaml
data:
  artifactRepository: |
    s3:
      bucket: <BUCKET>
      endpoint: <URL>
      insecure: true
      accessKeySecret:
        name: <MINIO_SECRET>
        key: <ACCESSKEY>
      secretKeySecret:
        name: <MINIO_SECRET>
        key: <SECRETKEY>
```

## Примеры использования Argo

### Простой пример с передачей контекста в публичный docker образ
#### Используемые ресурсы
1. Исполняемый Python файл [run.py](run.py)
2. Файл с входными данными [in.txt](in.txt)
3. Файл манифеста workflow [sample_dag_1.yaml](sample_dag_1.yaml)

#### Выполнение
используемые в коде переменные
* BUCKET: имя bucket'а в MinIO
* MINIO_SECRET: Имя secret раздела в argo, содержащего информацию об учётных данных экземпляра MinIO
* URL: адрес и порт для доступа к экземпляру MinIO

1. При необходимости создаём bucket в MinIO для хранения файлов
``` bash
mc mb minio/<BUCKET>
```
2. Помещаем в хранилище файлы, планируемые к использованию в workflow
``` bash
mc cp run.py minio/<BUCKET>
mc cp in.txt minio/<BUCKET>
```
3. Редактируем файл манифеста таким образом, что бы все разделы s3 выглядели следующим образом:
``` yaml
s3:
  bucket: <BUCKET>
  key: some_file_name # поле не изменяется
  endpoint: <URL>
  insecure: true
  accessKeySecret:
    name: <MINIO_SECRET>
    key: accesskey
  secretKeySecret:
    name: <MINIO_SECRET>
    key: secretkey
```
4. Запускаем манифест
``` bash
argo submit --watch sample_dag_1.yaml
```
Пример результата:
``` bash
Name:                sample-dag-jx5n7
Namespace:           argo
ServiceAccount:      unset (will run with the default ServiceAccount)
Status:              Succeeded
Conditions:
 PodRunning          False
 Completed           True
Created:             Thu Feb 24 02:53:45 +0300 (10 seconds ago)
Started:             Thu Feb 24 02:53:45 +0300 (10 seconds ago)
Finished:            Thu Feb 24 02:53:55 +0300 (now)
Duration:            10 seconds
Progress:            1/1
ResourcesDuration:   1s*(1 cpu),0s*(100Mi memory)

STEP                 TEMPLATE    PODNAME                      DURATION  MESSAGE
 ✔ sample-dag-jx5n7  sample-dag
 └─✔ model1-runner   model1      sample-dag-jx5n7-1696781470  5s
```
5. Смотрим логи исполнения:
``` bash
argo logs sample-dag-jx5n7
```
Пример результата:
``` bash
sample-dag-jx5n7-1696781470: time="2022-02-23T23:53:49.465Z" level=info msg="capturing logs" argo=true
sample-dag-jx5n7-1696781470: received digit 5
sample-dag-jx5n7-1696781470: sended digit 6
sample-dag-jx5n7-1696781470: time="2022-02-23T23:53:49.650Z" level=info msg="/out.txt -> /var/run/argo/outputs/artifacts/out.txt.tgz" argo=true
sample-dag-jx5n7-1696781470: time="2022-02-23T23:53:49.650Z" level=info msg="Taring /out.txt"
```
5. Проверяем исходящий файл:
``` bash
mc cp minio/<BUCKET>/out.txt .
cat out.txt
```
Пример результата:
``` bash
6
```

### Более сложный пример с передачей контекста в цепочку публичных docker образов и инференсом в torch
#### Используемые ресурсы
1. Исполняемый Python файл для инференса №1 [standalone_mock_3.py](containers/standalone_mock_3.py)
2. Исполняемый Python файл для инференса №1 [standalone_mock_7.py](containers/standalone_mock_7.py)
3. Файл с весами для инференса №1 [mock_3.pt](containers/weights/mock_3.pt) *
3. Файл с весами для инференса №1 [mock_7.pt](containers/weights/mock_7.pt) *
2. Файл с входными данными [in.pt](containers/weights/in.pt)
3. Файл манифеста workflow [sample_dag_4.yaml](sample_dag_4.yaml)

*веса для моделей генерируются в jupyter файле [test.ipynb](containers/test.ipynb). Для инференса №1 исползуется значение параметра model_size_factor = 3, для инференса №2 - model_size_factor = 7.

#### Выполнение
используемые в коде переменные
* BUCKET: имя bucket'а в MinIO
* MINIO_SECRET: Имя secret раздела в argo, содержащего информацию об учётных данных экземпляра MinIO
* URL: адрес и порт для доступа к экземпляру MinIO

1. При необходимости создаём bucket в MinIO для хранения файлов
``` bash
mc mb minio/<BUCKET>
```
2. Помещаем в хранилище файлы, планируемые к использованию в workflow
``` bash
mc cp containers/standalone_mock_3.py minio/<BUCKET>
mc cp containers/standalone_mock_7.py minio/<BUCKET>
mc cp containers/weights/mock_3.pt minio/<BUCKET>
mc cp containers/weights/mock_7.pt minio/<BUCKET>
mc cp in.pt minio/<BUCKET>
```
3. Редактируем файл манифеста таким образом, что бы все разделы s3 выглядели следующим образом:
``` yaml
s3:
  bucket: <BUCKET>
  key: some_file_name # поле не изменяется
  endpoint: <URL>
  insecure: true
  accessKeySecret:
    name: <MINIO_SECRET>
    key: accesskey
  secretKeySecret:
    name: <MINIO_SECRET>
    key: secretkey
```
4. Запускаем манифест
``` bash
argo submit --watch sample_dag_4.yaml
```
Пример результата:
``` bash
Name:                sample-dag-slmhn
Namespace:           argo
ServiceAccount:      unset (will run with the default ServiceAccount)
Status:              Succeeded
Conditions:
 PodRunning          False
 Completed           True
Created:             Thu Feb 24 03:11:56 +0300 (31 seconds ago)
Started:             Thu Feb 24 03:11:56 +0300 (31 seconds ago)
Finished:            Thu Feb 24 03:12:27 +0300 (now)
Duration:            31 seconds
Progress:            2/2
ResourcesDuration:   11s*(1 cpu),6s*(100Mi memory)

STEP                 TEMPLATE    PODNAME                      DURATION  MESSAGE
 ✔ sample-dag-slmhn  sample-dag
 ├─✔ model1-runner   model1      sample-dag-slmhn-2101208660  5s
 └─✔ model2-runner   model2      sample-dag-slmhn-3015997719  11s
 ```
 5. Смотрим логи исполнения:
``` bash
argo logs sample-dag-slmhn
```
Пример результата:
``` bash
sample-dag-slmhn-2101208660: time="2022-02-24T00:12:00.114Z" level=info msg="capturing logs" argo=true
sample-dag-slmhn-2101208660: The mock model is initialized (Size: 3, Add: 1). Weights size is 38.17 Mb
sample-dag-slmhn-2101208660: Incoming tensor mean is 1.0
sample-dag-slmhn-2101208660: Resulted tensor mean is 2.0
sample-dag-slmhn-2101208660: time="2022-02-24T00:12:01.153Z" level=info msg="/out1.pt -> /var/run/argo/outputs/artifacts/out1.pt.tgz" argo=true
sample-dag-slmhn-2101208660: time="2022-02-24T00:12:01.153Z" level=info msg="Taring /out1.pt"
sample-dag-slmhn-3015997719: time="2022-02-24T00:12:14.193Z" level=info msg="capturing logs" argo=true
sample-dag-slmhn-3015997719: The mock model is initialized (Size: 7, Add: 1). Weights size is 462.256 Mb
sample-dag-slmhn-3015997719: Incoming tensor mean is 2.0
sample-dag-slmhn-3015997719: Resulted tensor mean is 3.0
sample-dag-slmhn-3015997719: time="2022-02-24T00:12:16.657Z" level=info msg="/out2.pt -> /var/run/argo/outputs/artifacts/out2.pt.tgz" argo=true
sample-dag-slmhn-3015997719: time="2022-02-24T00:12:16.657Z" level=info msg="Taring /out2.pt"
```
5. Проверяем исходящий файл:

``` bash
mc cp minio/<BUCKET>/out2.pt .
```
Пример проверки с использованием Python
``` bash
Python 3.8.10 (default, Nov 26 2021, 20:14:08)
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> out = torch.load('out2.pt')
>>> out.mean()
tensor(3.)
```

## Известные проблемы
Нестабильно работает выполнение workflow. В процессе выполнения возникает ошибка сохранения исходящего файла в MinIO: Error (exit code 1): failed to put file: The Access Key Id you provided does not exist in our records. Это происходит из-за того что происходит попытка сохранить запакованный в tgz файл вместо указанного в манифесте. Я попытался это исправить добавив параметр archive: none: {} в код манифеста, это частично помогло, но нестабильность не пропала, периодически выполнение манифеста прерывается (при этом исходящий файл успешно сохраняется в хранилище).