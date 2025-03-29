define([
  'sources/gettext',
  'sources/url_for',
  'react',
  'react-dom',
  'pgadmin.browser.endpoints',
  'pgadmin.tools.translations',
  'pgadmin.SecurityPages.MfaRegisterPage'
], function(gettext, url_for, React, ReactDOM, endpoints, translations, MfaRegisterPage) {
  return {
    renderSecurityPage: function(pageName, pageProps, otherProps) {
      const root = ReactDOM.createRoot(document.getElementById('root'));
      
      if (pageName === 'mfa_register') {
        root.render(
          <MfaRegisterPage {...pageProps} {...otherProps} />
        );
      }
    },
  };
}); 