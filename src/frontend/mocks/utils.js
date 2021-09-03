/**
 * @description
 * @author liguanlin<liguanlin@4paradigm.com>
 */
function success() {
  return {
    status: 'success',
    message: '',
  }
}
function failure() {
  return {
    status: 'failure',
    message: 'system error',
  }
}
module.exports = {
  success,
  failure
}
