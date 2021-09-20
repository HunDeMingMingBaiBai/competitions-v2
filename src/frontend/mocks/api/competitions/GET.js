/**
 * @description
 * @author liguanlin<liguanlin@4paradigm.com>
 */
/**
 * @description competitions search mockup
 * @author liguanlin<liguanlin@4paradigm.com>
 */
const fs = require('fs');
const path = require('path')
const utils = require('../../utils');

module.exports = function (request, response) {
  let rawData = fs.readFileSync(path.join(__dirname, 'GET.json'));
  const competitions = JSON.parse(rawData);
  let data = [];
  if (request.query.search) {
    data = competitions.filter(item => JSON.stringify(item).indexOf(request.query.search) >= 0)
  }
  if (request.query.mine && request.query.type == 'any') {
    rawData = fs.readFileSync(path.join(__dirname, 'GET_Running.json'))
    data = JSON.parse(rawData);
  }
  if (request.query.participate_in) {
    rawData = fs.readFileSync(path.join(__dirname, 'GET_Participate_in.json'))
    data = JSON.parse(rawData);
  }
  response.json({ ...utils.success(), data })
}
