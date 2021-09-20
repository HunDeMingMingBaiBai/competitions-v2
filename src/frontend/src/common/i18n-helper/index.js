/**
 * @description i18n helper
 * @author liguanlin<liguanlin@4paradigm.com>
 */
export * from 'react-intl';
export { LANG, getLocale, setLocale, defaultLocale, initLocale, LOCALE, ILANG, removeLocale } from './i18n';
export { initDateLocale, dateFormat } from './date';
export { plainCreateIntl } from './intl';
export { default as Translation } from './translation';
export { setHTMLLang, setTitle, getHTMLLang, getTitle } from './init';
