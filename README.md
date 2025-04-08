# Website Checker Bot

[**Website Checker Bot**](https://t.me/fswebsitecheckerbot) is a free Russian-language Telegram bot designed to check websites for security.

## Functionality

### The bot supports the following functionality:

- Displaying the website security percentage
- Sending website scripts (HTML, CSS, JavaScript)
- Displaying the text contained on the website
- Displaying website headers
- Displaying links contained on the website
- Displaying website meta tags
- Checking for the presence of security-related headers:
  - `Content-Security-Policy`
  - `X-Frame-Options`
  - `X-XSS-Protection`
  - `Strict-Transport-Security`

The bot calculates the security percentage by checking the website for the presence of the above website security headers.

### Sample output for the [Google](https://google.com) website

> Status code: 200  
> Security percentage: 70%  
> HTTPS: The site uses HTTPS  
> Security headers:  
> Content-Security-Policy: Content-Security-Policy header is missing  
> X-Frame-Options: Present  
> X-XSS-Protection: Present  
> Strict-Transport-Security: Strict-Transport-Security header is missing

## Contacts
- Developer: **Flarosoft**
- Email: [flarosoft.dev@gmail.com](mailto:flarosoft.dev@gmail.com)
- Developer's Telegram channel: [@flarosoftdev](https://t.me/flarosoftdev)
- Archive with Telegram bots from Flarosoft: [@flarosoftbots](https://t.me/flarosoftbots)
- GitHub: [Flarosoft Development](https://github.com/flarosoftdev)
- Developer's website: [flarosoft.pages.dev](https://flarosoft.pages.dev)
