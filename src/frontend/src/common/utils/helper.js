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
