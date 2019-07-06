Vue.use(iview);
Vue.prototype.$copy = function (val) {
    return JSON.parse(JSON.stringify(val))
};
Vue.prototype.$apply = function (data) {
    return Object.assign({}, data, data);
};
axios.defaults.baseURL = site_url;
Vue.prototype.$http = axios;

axios.interceptors.request.use(
    config => {
        if (config.data && config.data.noload) {
            delete config.data.noload
        }
        else {
            vm.$Spin.show();
        }
        return config;
    },
    err => {
        return Promise.reject(err);
    }
);

axios.interceptors.response.use(response => {
    if (response.status !== 200) {
        return {
            code: response.status,
            message: '请求异常，请刷新重试',
            result: false
        }
    }
    vm.$Spin.hide();
    return response.data
});

var getQueryVariable = function (variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) {
            return pair[1];
        }
    }
    return (false);
}