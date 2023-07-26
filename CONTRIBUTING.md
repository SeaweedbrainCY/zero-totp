# Contribution Guidelines for Zero-TOTP Project

Thank you for your interest in contributing to Zero-TOTP! We value security above all, and your contributions play a crucial role in making this project even better. Please take a moment to read and follow these guidelines to ensure a smooth and effective contribution process.

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
    - [Fork the Repository](#fork-the-repository)
    - [Set up the Project](#set-up-the-project)
3. [Contribution Process](#contribution-process)
    - [Issue Tracker](#issue-tracker)
    - [Branching](#branching)
    - [Code Style](#code-style)
    - [Testing](#testing)
4. [Submitting Pull Requests](#submitting-pull-requests)
5. [Security](#security)
6. [Community and Communication](#community-and-communication)
7. [Acknowledgements](#acknowledgements)
8. [License](#license)

## Introduction

Zero-TOTP is an open-source project focused on providing a secure and reliable implementation of Time-based One-Time Password (TOTP) client. We welcome contributions from the community to enhance its functionality, security, and usability.

## Getting Started

### Fork the Repository

Before you start contributing, make sure to fork the Zero-TOTP repository to your GitHub account. You will be working on your forked repository and submitting pull requests from there.

### Set up the Project

1. Clone your forked repository to your local machine:
```
git clone https://github.com/your-username/zero-totp.git
cd zero-totp
```
2. Install the required dependencies:
```
make install_frontend
make install_api
```
3. Define your env variables :
Create a .env file at the root project and define these variables :
```
export DATABASE_URI="mysql://<mysqlUser>:<mysqlPassword>@127.0.0.1:3306/zero_totp"
export ENVIRONMENT="DEV"
export JWT_SECRET=
export MYSQL_ROOT_PASSWORD=
export MYSQL_DATABASE=zero_totp
export MYSQL_USER=
export MYSQL_PASSWORD=
```
4. Run the API, frontend and database :
```
make run_pai
make run_frontend
docker compose up database
```
## Contribution Process

### Issue Tracker

If you want to work on a new feature, bug fix, or other enhancements, please check the [Issue Tracker](https://github.com/zero-totp/zero-totp/issues) first. It's possible that someone else is already working on something similar or that the issue has already been addressed.

If you find a new issue or want to suggest an enhancement, please open a new issue on the Issue Tracker. Provide a clear description and, if applicable, steps to reproduce the problem.

### Branching

For every contribution, create a new branch with a descriptive name that summarizes the changes you plan to make. Use lowercase letters and dashes to separate words, for example:
```
git checkout -b feature/add-qr-code-generation
```

### Code Style

We follow a consistent coding style to ensure readability and maintainability. Please follow these guidelines:
- Use meaningful variable and function names.
- Write clear comments and documentation as needed.
- Maintain a consistent indentation style (e.g., 2 spaces).

### Testing

Your contributions should include appropriate test cases. Ensure that all tests pass before submitting a pull request.

## Submitting Pull Requests

When you're ready to submit your changes, follow these steps:
1. Commit your changes with a descriptive commit message.
2. Push your changes to your forked repository:
```
git push origin your-branch-name
```
3. Go to the Zero-TOTP repository on GitHub and create a new pull request from your branch.
4. Provide a clear title and description for your pull request, including any relevant information about the changes you made.

## Security

Security is our top priority. If you discover any security vulnerabilities or potential issues, please **DO NOT** open a public issue. Instead, contact us directly at security@zero-totp.com with all the details. We appreciate your responsible disclosure.

## Community and Communication

We value a friendly and inclusive community. Be respectful and considerate when communicating with other contributors. If you have questions or need help, you can reach out to us on our [Discord channel](https://discord.gg/zerototp).

## Acknowledgements

We appreciate all contributions to Zero-TOTP, and we recognize and acknowledge everyone's effort and time. Contributors will be listed in the project's contributors section.

## License

By contributing to Zero-TOTP, you agree that your contributions will be licensed under the [GPL-3.0 license](https://github.com/zero-totp/zero-totp/blob/main/LICENSE).

---

