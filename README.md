# QuizzReviewInterface

A Flask web application that provides an interface to review and edit quiz questions stored in YAML format.

## Features

- Review, edit, and navigate through quiz questions.
- Questions are organized with attributes like course, section, chapter, difficulty, duration, and more.
- Data is saved in a structured YAML format.

## Setup

### Prerequisites

- Python 3
- pip3

### Installation Steps

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Asi0Flammeus/QuizzReviewInterface.git
    cd QuizzReviewInterface
    ```

2. **Create a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    ```

3. **Activate the Virtual Environment:**
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4. **Install the Required Packages:**
    ```bash
    pip3 install -r requirements.txt
    ```

5. **Run the Application:**
    ```bash
    python3 app.py
    ```

Visit `http://127.0.0.1:5000/` in your browser to access the QuizzReviewInterface.

## Usage

- Browse to the main page and navigate through quiz questions using the provided buttons.
- Edit question details and save changes as needed.

## Contributing

Contributions are welcome. To contribute, please fork the repository and create a pull request with your changes. Ensure that changes are tested and existing functionality is maintained.

Here we promote [*Value for Value*](https://dergigi.com/2021/12/30/the-freedom-of-value/) model so if you find value in this humble script tips are welcomed via [LN](https://getalby.com/p/asi0) or by scanning directly this QR code with a Lightning wallet 👇.

<img src="./figure/LN-address-asi0-tip.png" width="175">

## License

This project is governed by the MIT License. For more information, refer to the [LICENSE file](./license.md).
