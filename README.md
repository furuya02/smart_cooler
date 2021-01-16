# smart_cooler
レジなし無人販売冷蔵庫


# setup
```
$ git clone https://github.com/furuya02/smart_cooler.git
$ cd smart_cooler
```

### CDK
※ Amazon Pay用のキーペアは、含まれていません

```
$ cd cdk/smart_cooler
$ yarn;cd lib/lambda;yarn; cd../..
$ tsc
$ cdk deploy
```

### Jetson nano
※ DLR用のモデルは、含まれていません
```
$ scp -r jetson user@hostname:~
```
