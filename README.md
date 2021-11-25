# Tugas Besar 2 Jarkom
> Implementasi TCP over UDP

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Code examples](#code-examples)
* [Features](#features)
* [Status](#status)
* [Contact](#contact)

## General info
Project ini mensimulasikan TCP menggunakan UDP dengan menggunakan library yang disediakan oleh python.

## Technologies
* Python
* Struct
* Socket
## Setup
1. Install python (rekomendasi yang terbaru) pada link [ini](https://www.python.org/downloads/)
3. Lakukan git clone repository ini dengan mengetikkan di terminal atau git bash
```bash
git clone https://gitlab.informatika.org/widyaput/tcp-over-udp.git
```

## Code Examples
Show examples of usage:
1. Masuk ke folder hasil clone git repository
2. Jalankan server dengan perintah di bawah ini. Tambahkan flag "-s" jika ingin mengirim metadata.
```bash
python Server.py 5005 {nama file}
```

3. Jalankan client dengan perintah di bawah ini. Jika server dijalankan dengan flag "-s", sebaiknya client juga dijalankan dengan flag "-s". Begitu pula sebaliknya (ada atau tidak ada keduanya).
```bash
python Client.py {port selain 5005} {nama file tujuan}
```
4. Jalankan interaksi pada server jika menginginkan lebih dari 1 client


## Features
* Fitur pengiriman file dengan TCP-UDP
* Fitur pengiriman metadata yang dapat diubah-ubah tergantung penggunaan flag -s (send metadata)
* Fitur pengoptimalan ram karena menggunakan fungsi seek() untuk melewati offset dari file

## Status
Project is: _finished_

## Contact
Created by:
1. M Fahmi Alamsyah (13519077)
2. Widya Anugrah Putra (13519105)
3. Kadek Surya Mahardika (13519165)

Feel free to contact us!
