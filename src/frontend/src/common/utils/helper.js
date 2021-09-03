/**
 * @description helper functions
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import { uniqueId } from 'lodash';

/**
 * 根据前缀生成唯一的 key
 *
 * @param {string} prefix 前缀
 * @return {string} 返回唯一的 key
 */
export function genRowKey(prefix) {
  return uniqueId(`${prefix}_`);
}

/**
 * parse router as xxx/:xx to url
 * @param {string} _url
 * @param {object} params
 * @param {object} data
 * @return {object}
 */
export const parseUrl = function ({ url: _url, params, data }) {

  // if url router as xxx/:xx, replace params
  let url = _url.replace(/:([a-zA-Z0-9]+)/g, (sub, field) => {
    if (field in params) {
      const value = params[field];
      // remove matched value from params
      delete params[field];
      return value;
    } else if (field in data) {
      const value = postData[field];
      delete data[field];
      return value;
    }
    throw new Error(`Cannot found params "${field}" to repalce url pattern "${pattern}"`)
  })

  return {
    url,
    params,
    data
  }
}
