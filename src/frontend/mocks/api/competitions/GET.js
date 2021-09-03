/**
 * @description competitions search mockup
 * @author liguanlin<liguanlin@4paradigm.com>
 */
const fs = require('fs');
const path = require('path')
const utils = require('../../utils');

module.exports = function (request, response) {
  const rawData = fs.readFileSync(path.join(__dirname, 'GET.json'));
  const competitions = JSON.parse(rawData);
  let data = [];
  if (request.query.search) {
    data = competitions.filter(item => JSON.stringify(item).indexOf(request.query.search) >= 0)
  }
  response.json({ ...utils.success(), data })
}
