<div align="center">
  <a href="https://revenut.com/" style="color: black;">
    <img alt="revenut" src="https://github.com/hbcondo/revenut-app/raw/main/docs/assets/Revenut-logo-128x128.png" width="128" height="128">
    <h1>Revenut</h1>
  </a>
</div>

<div align="center">
  <!-- iOS -->
  <img alt="Supports Expo iOS" longdesc="Supports Expo iOS" src="https://img.shields.io/badge/iOS-4630EB.svg?style=flat-square&logo=APPLE&labelColor=999999&logoColor=fff" />
  <!-- Android -->
  <img alt="Supports Expo Android" longdesc="Supports Expo Android" src="https://img.shields.io/badge/Android-4630EB.svg?style=flat-square&logo=ANDROID&labelColor=A4C639&logoColor=fff" />
  <!-- Web -->
  <img alt="Supports Expo Web" longdesc="Supports Expo Web" src="https://img.shields.io/badge/web-4630EB.svg?style=flat-square&logo=GOOGLE-CHROME&labelColor=4285F4&logoColor=fff" />

  <h3 align="center">SaaS Metrics in a Nutshell</h3>
  <a href="https://api.revenut.com/docs">OpenAPI</a> | <a href="https://github.com/hbcondo/revenut-app/wiki">Wiki</a> | <a href="https://app.revenut.com">Demo</a>
</div>

---
> By Amar Kota - [Hire me](https://amarkota.com/resume)

![revenut-api](https://github.com/hbcondo/revenut-app/blob/main/docs/assets/Revenut-cURL.png?raw=true)

## 🧐 About
This is an API project that delivers the RESTful endpoints that power the SaaS analytics web + mobile app **Revenut** at [app.revenut.com](https://app.revenut.com). 

> [!NOTE]
> Please read https://github.com/hbcondo/revenut-app before getting started.

## 🏁 Getting Started
These instructions will get you a copy of the API up and running on your local machine for development and testing purposes.

### Prerequisites
- [Python](https://www.python.org)
- [Stripe](https://stripe.com)

### Installation
```cli
git clone https://github.com/hbcondo/revenut-api.git
cd revenut-api
virtulenv env
source env/bin/activate
pip install -r requirements.txt
hypercorn app/main:app --reload
```

### Environment variables
Create an ```.env``` file in the root with these keys:
- STRIPE_API_KEY
- STRIPE_CLIENT_ID
- STRIPE_ACCOUNT_ID (optional)

## 🔧 Running the tests
```cli
(.venv) revenut-api % pytest
=========================== test session starts ===========================
platform darwin -- Python 3.11.4, pytest-7.4.0, pluggy-1.2.0
rootdir: /revenut-api
plugins: anyio-3.6.2
collected 2 items                                                         

app/test_main.py ..                                                 [100%]

============================ 2 passed in 0.40s ============================
```

## ⛏️ Built Using
- [Python](https://www.python.org)
- [FastAPI](https://fastapi.tiangolo.com)
- [OpenAPI](https://www.openapis.org)

## 👪 Contributing
If you like Revenut, please star this repo. If you want to make Revenut better, feel free to submit a PR, log an issue or [contact me](https://amarkota.com/contact) directly.

## 🔖 License
The Revenut source code is made available under the [**Apache 2.0 license**](LICENSE).

## ✍️ Authors
- [@hbcondo](https://github.com/hbcondo) - dea & initial work

## 🎉 Acknowledgements
https://stripe.com/docs/api
