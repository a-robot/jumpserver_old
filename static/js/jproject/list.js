var app = angular.module('myApp', []).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});


app.controller('AssertDetailCtrl', function($scope, $http) {
    get_project_json($scope, $http);
    $scope.connect_click = connect;
});


function get_project_json($scope, $http){
    var url = '/jproject/project/list/json';
    $http.get(url).then(function(data){
        data = data.data;
        init_project_tree($scope, data);
        init_host_data($scope, data);
    }).catch(function(e){
        console.log(e);
    });
}


function init_project_tree($scope, data){
    var projects = data.projects;
    var source = gen_project_source(projects);
    $("#tree").fancytree({
        source: source,
        click: function(e, data){
            tree_click($scope, e, data);
        }
    });
}


function init_host_data($scope, data){
    var hosts = [];
    $.each(data.projects, function(_i, project){
        $.each(project.app_modules, function(_i, app_module){
            $.each(app_module.hosts, function(_i, host){
                hosts.push(host);
            });
        });
    });

    var host_data = {};
    $.each(hosts, function(index, host){
        host_data[host.id] = host;
    });

    $scope.host_data = host_data;
}


function tree_click($scope, e, data){
    if(!data.node.isFolder()){
        $scope.selected_asset = $scope.host_data[data.node.key];
        $scope.$apply();
        $('.host-detail').css('display', 'inline-block');
    }
}


function connect(id, hostname){
    var url='/jperm/role/get/?id=' + id; // 获取用户有权限的角色
    var new_url = '/terminal/?id=' + id + '&role='; // webterminal socket url
    $.ajax({
        type: 'GET',
        url: url,
        data: {},
        success: function(data){
            var dataArray = data.split(',');
            if (data == 'error' || data == '' || data == null || data == undefined){
                layer.alert('没有授权系统用户')
            }
            else if (dataArray.length == 1 && data != 'error' && navigator.platform == 'Win32'){
                 window.open(new_url+data, "_blank");
            }  else if (dataArray.length == 1 && data != 'error'){
                window.open(new_url+data, '_blank');
            }
            else {
                aUrl = '';
                $.each(dataArray, function(index, value){
                    aUrl += '<a onclick="windowOpen(this); return false" class="btn btn-xs btn-primary newa" href=' + new_url + value + ' value=' + hostname +  '>' + value  + '</a> '
                });
                console.log(aUrl);
                layer.alert(aUrl, {
                    skin: 'layui-layer-molv',
                    title: '授权多个系统用户，请选择一个连接',
                    shade: false,
                    closeBtn: 0
                })
            }
        }
    });
}


function gen_project_source(projects){
    var source = [];
    $.each(projects, function(_i, project){
        var project_name = project.name;
        var tree_project = {title: project_name, folder: true, expanded: true};
        tree_project.children = gen_app_moudule_source(project.app_modules);
        source.push(tree_project);
    });
    return source;
}


function gen_app_moudule_source(app_modules){
    var source = [];
    $.each(app_modules, function(_i, app_module){
        var tree_app_module = {title: app_module.name, folder: true, expanded: true}
        tree_app_module.children = gen_host_source(app_module.hosts);
        source.push(tree_app_module);
    });
    return source;
}


function gen_host_source(hosts){
    var source = [];
    $.each(hosts, function(_i, host){
        var tree_host = {
            title: host.hostname,
            key: host.id,
            type: 'host',
        }
        source.push(tree_host);
    });
    return source;
}
