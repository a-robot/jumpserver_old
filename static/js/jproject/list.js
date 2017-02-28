$(document).ready();

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
    var source = [];
    $.each(data, function(project_name, project){
        if (project_name) {
            var tree_project = {title: project_name, folder: true, children: []};
            $.each(project['assets'], function(index, asset){
                var tree_asset = {
                    title: asset['hostname'],
                    key: asset['id'],
                    type: 'host',
                }
                tree_project['children'].push(tree_asset);
            });
            source.push(tree_project);
        }
    });
    $("#tree").fancytree({
        source: source,
        click: function(e, data){
            tree_click($scope, e, data);
        }
    });
}

function init_host_data($scope, data){
    var hosts = [];
    $.each(data, function(pn, p){
        if(pn){
            hosts = hosts.concat(p.assets);
        }
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
        console.log($scope.selected_asset);
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
