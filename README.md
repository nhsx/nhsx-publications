# The nhsx.io theme

**nhsx.io** is a Jekyll theme for GitHub Pages. You can [preview the theme](https://nhsx.github.io/nhsx-io-theme/) to see what it looks like

## Usage

To use the nhsx.io theme:

1. Add the following to your site's `_config.yml`:

    ```yml
    remote_theme: nhsx/nhsx-io-theme
    ```

## Customizing

### Configuration variables

nhsx.io will respect the following variables, if set in your site's `_config.yml`:

```yml
description: [A short description of your site's purpose]
```

Additionally, you may choose to set the following optional variables:

```yml
show_downloads: ["true" or "false" to indicate whether to provide a download URL]
google_analytics: [Your Google Analytics tracking ID]
```

### Stylesheet

If you'd like to add your own custom styles:

1. Create a file called `/assets/css/style.scss` in your site
2. Add the following content to the top of the file, exactly as shown:
    ```scss
    ---
    ---

    @import "{{ site.theme }}";
    ```
3. Add any custom CSS (or Sass, including imports) you'd like immediately after the `@import` line

### Layouts

If you'd like to change the theme's HTML layout:

1. [Copy the original template](https://github.com/nhsx/nhsx-io-theme/blob/master/_layouts/default.html) from the theme's repository<br />(*Pro-tip: click "raw" to make copying easier*)
2. Create a file called `/_layouts/default.html` in your site
3. Paste the default layout content copied in the first step
4. Customize the layout as you'd like

## Contributing

Interested in contributing to nhsx.io? See [the CONTRIBUTING file](docs/CONTRIBUTING.md) for instructions on how to contribute.
