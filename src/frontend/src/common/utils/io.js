/**
 * @description Customized Axios Request
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import axios from 'axios';
// import { Modal } from 'antd';
import { isFunction } from 'lodash';
// import mock from '../mock';
import { parseUrl } from './helper';
import { push } from './history';

// const DEFAULT_ERROR_MESSAGE = '抱歉，请求错误'
const SERVER_ERROR = getGlobalError('服务器错误');
const PARSE_ERROR = getGlobalError('数据解析失败');
// const SCHEMA_ERROR = getGlobalError('数据格式错误');
const NETWORK_ERROR = getGlobalError('网络错误');

/**
 * 生成全局错误对象
 *
 * @param {string} message 错误提示信息
 * @return {Object} 全局错误对象
 */
function getGlobalError(message) {
  return {
    status: 'failed',
    message
  };
}

/**
 * 处理服务端响应成功的情况
 *
 * @param {meta.Promise} response 响应的Promise
 * @return {meta.Promise} 处理后的Promise
 */
function requestSuccessHandler(response) {
  if (response.status !== 'success' && response.status.code !== 200) {
    let message = response.message;
    if (message) {
      // Modal.error({
      //   title: '系统提示',
      //   content: message
      // });
    }
    return Promise.reject(response).catch(() => ({ 'error': true }));
  }
  return Promise.resolve(response);
}

/**
 * 处理服务端响应失败的情况
 * 转换为成功响应，返回错误提示处理
 *
 * @param {meta.Promise} error 响应的Promise
 * @return {meta.Promise} 处理后的Promise
 */
function requestFailureHandler(error) {
  const response = error.response;
  let errorType = null;
  if (response) {
    const status = response.status;
    const data = response.data;
    if (status < 200 || (status >= 300 && status !== 304)) { // 服务器没有正常返回
      errorType = SERVER_ERROR;
      if (data && data.detail) {
        errorType = getGlobalError(JSON.stringify(response.data.detail[0]))
      }
    } else if (status === 403) {
      // Modal.warning({
      //   title: '系统提示',
      //   content: '系统长时间未操作，登录超时，请重新登录'
      // });
      setTimeout(() => push('/login'), 500);
      return Promise.reject(error).catch(() => ({ 'error': true }));
    } else {
      errorType = PARSE_ERROR;
    }
  } else if (error.message) {
    errorType = getGlobalError(error.message);
  } else {
    errorType = NETWORK_ERROR;
  }
  requestSuccessHandler(errorType);
}

class IO {
  axios = axios.create({
    headers: {
      'Content-Type': 'application/json;charset=utf-8'
    }
  });

  apis = {};
  hooks = {};
  me = null;

  constructor() {
    this.axios.interceptors.response.use(
      response => {
        // IE9 不支持 responseType 配置，所以 response.data 始终都不会存在，
        // 手动从 response.request.responseText 中 parse。
        const data = response.data || JSON.parse(response.request.responseText);
        return requestSuccessHandler.call(this, data)
      },
      requestFailureHandler.bind(this)
    );
  }

  create(scope, items) {
    for (const key of Object.keys(items)) {
      const config = items[key];
      if (!scope) {
        console.warn(`SCOPE has not been given in "${key}"'s mock file, this may cause url conflict.`)
      }
      if (!this.apis[scope]) {
        this.apis[scope] = {};
      }
      this.apis[scope][key] = function (_extraConfig) {
        let extraConfig = _extraConfig;
        if (isFunction(config.transformer)) {
          extraConfig = config.transformer(_extraConfig);
        }
        return this.request({
          ...config,
          ...parseUrl({ url: config.url, ...extraConfig })
        });
      }
      this.apis[scope][key] = this.apis[scope][key].bind(this);
    }
  }

  getApis(file) {
    return { ...this.apis[file] };
  }

  request(...args) {
    return this.axios(...args);
  }
}

const io = new IO();

export default io;
