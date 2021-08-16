/**
 * @file api
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import io from '../utils/io';
// scope should be same with filename
const SCOPE = 'lab';

io.create(SCOPE, {
  predict: {
    method: 'post',
    url: '/lab/ocr/predict/:type',
  },
  demo: {
    url: '/lab/ocr/demo',
  },
  scenes: {
    url: '/lab/ocr/scenes',
  },
});
const labApi = io.getApis(SCOPE);
export default labApi;
