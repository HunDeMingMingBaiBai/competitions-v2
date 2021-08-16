/**
 * @file Customized Axios Request
 * @author liguanlin<liguanlin@4paradigm.com>
 */

import axios from 'axios';
import { Modal } from 'antd';
import { push } from '../history';
import mock from '../mock';
import { parseUrl } from '../helper';
/**
 * 生成全局错误对象
 *
 * @param {string} message 错误提示信息
 * @return {Object} 全局错误对象
 */
function getGlobalError(message) {
  return {
    status: 'failed',
    message,
  };
}

const SERVER_ERROR = getGlobalError('服务器错误');
const PARSE_ERROR = getGlobalError('数据解析失败');
const NETWORK_ERROR = getGlobalError('网络错误');

/**
 * 处理服务端响应成功的情况
 *
 * @param {meta.Promise} response 响应的Promise
 * @return {meta.Promise} 处理后的Promise
 */
function requestSuccessHandler(response) {
  if (response.status !== 'success') {
    const { message } = response;
    if (message) {
      Modal.error({
        title: '系统提示',
        content: message,
      });
    }
    return Promise.reject(message).catch(() => ({ error: true }));
  }
  return Promise.resolve(response.data);
}

/**
 * 处理服务端响应失败的情况
 * 转换为成功响应，返回错误提示处理
 *
 * @param {meta.Promise} error 响应的Promise
 * @return {meta.Promise} 处理后的Promise
 */
function requestFailureHandler(error) {
  const { response } = error;
  let errorType;
  if (response) {
    const { status } = response;
    if (status < 200 || (status >= 300 && status !== 304)) { // 服务器没有正常返回
      errorType = SERVER_ERROR;
    } else if (status === 403) {
      Modal.warning({
        title: '系统提示',
        content: '系统长时间未操作，登录超时，请重新登录',
      });
      setTimeout(() => push('/login'), 500);
      return Promise.reject(error).catch(() => ({ error: true }));
    } else {
      errorType = PARSE_ERROR;
    }
  } else if (error.message) {
    errorType = getGlobalError(error.message);
  } else {
    errorType = NETWORK_ERROR;
  }
  requestSuccessHandler(errorType);
  return errorType;
}

export class IO {
    axios = axios.create({
      headers: {
        'Content-Type': 'application/json;charset=utf-8',
      },
    });

    apis = {};

    hooks = {};

    me = null;

    /* eslint no-param-reassign: ["error", { "props": false }] */
    constructor() {
      this.axios.interceptors.request.use(mock.interceptor);
      this.axios.interceptors.request.use((config) => {
        if (!config.meta) {
          config.meta = {};
        }
        return config;
      });
      this.axios.interceptors.response.use(
        (response) => {
          // IE9 不支持 responseType 配置，所以 response.data 始终都不会存在，
          // 手动从 response.request.responseText 中 parse。
          const data = response.data || JSON.parse(response.request.responseText);
          return requestSuccessHandler.call(this, data);
        },
        requestFailureHandler.bind(this),
      );
    }

    request(...args) {
      return this.axios(...args);
    }

    create(scope, items) {
      for (const key of Object.keys(items)) {
        const config = items[key];
        if (!scope) {
          console.warn(`SCOPE has not been given in "${key}"'s mock file, this may cause url conflict.`);
        }
        if (!this.apis[scope]) {
          this.apis[scope] = {};
        }
        this.apis[scope][key] = extraConfig => (this.request({
          ...config,
          ...parseUrl(config.url, extraConfig.params, extraConfig.data),
        }));
        this.apis[scope][key] = this.apis[scope][key].bind(this);
      }
    }

    getApis(file) {
      return { ...this.apis[file] };
    }
}

export default new IO();
