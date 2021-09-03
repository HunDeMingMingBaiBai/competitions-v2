/**
 * @description
 * @author liguanlin<liguanlin@4paradigm.com>
 */
import io from './utils/io';
const HOME = 'home';

io.create(HOME, {
  competitionsFrontpage: {
    method: 'get',
    url: '/api/competitions/front_page',
  },
  generalStatus: {
    method: 'get',
    url: '/api/get_general_status'
  },
  competitions: {
    method: 'get',
    url: '/api/competitions'
  }
});

export const homeApi = io.getApis(HOME);
