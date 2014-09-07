(function (exports, ng) {
    'use strict';

    /**
     * App
     *
     */
    exports.mdwiki = ng.module('mdwiki', ['ngRoute']);

    /**
     * Route provider
     *
     */
    exports.mdwiki.config(['$routeProvider',
        function ($routeProvider)
    {
        $routeProvider.
            when('/:filename*', {
                template   : '<div ng-bind-html="contents"></div>',
                controller : 'FileCtrl'
            });
    }]);

    /**
     * File Service Factory
     *
     */
    exports.mdwiki.factory('fileService',
        ['$http', '$sce', '$q',
            function ($http, $sce, $q)
    {
        var fileService = {

            /**
             * Get file info for given path from backend
             *
             */
            getFile: function (fileName) {
                var promise = $http.get('/file/' + fileName)
                    .then(function (transport) {
                        if (transport.data.errors !== undefined
                                && transport.data.errors.length > 0) {
                            return $q.reject(transport.data.errors);
                        }
                        return transport.data;
                    });
                return promise;
            }

        };
        return fileService;
    }]);

    /**
     * File Controller
     *
     */
    exports.mdwiki.controller('FileCtrl',
        ['fileService', '$scope', '$routeParams', '$sce',
            function (fileService, $scope, $routeParams, $sce)
    {
        fileService.getFile($routeParams.filename).then(function (file) {
            if (file.type == 'file') {
                $scope.contents = $sce.trustAsHtml(file.contents);
            }
        }).catch(function (errors) {
            //TODO: pass errors to message controller
            console.log(errors);
        });
    }]);

    /**
     * Tree Controller
     *
     */
    exports.mdwiki.controller('TreeCtrl',
        ['fileService', '$scope',
            function (fileService, $scope)
    {
        $scope.toggleOpen = function (dir, parent) {

            // Check if dir contents are already loaded
            if (parent !== undefined
                    && parent.subdirs !== undefined
                    && parent.subdirs[dir] !== undefined) {
                // Toggle openness
                parent.subdirs[dir].isOpen = !parent.subdirs[dir].isOpen;
                return;
            }

            // Load dir contents
            var parentPath = parent === undefined ? '' : parent.path + '/';
            var path = parentPath + dir;
            fileService.getFile(path).then(function (node) {
                if (node.type == 'dir') {
                    node.path = path;
                    if (parent === undefined) {
                        $scope.root = node;
                    } else {
                        if (parent.subdirs === undefined) {
                            parent.subdirs = {};
                        }
                        parent.subdirs[dir] = node;
                    }
                    node.isOpen = true;
                }
            }).catch(function (errors) {
                //TODO: pass errors to message controller
                console.log(errors);
            });
        };
        $scope.toggleOpen('');
    }]);

    /**
     * Tree directive
     *
     */
    exports.mdwiki.directive('tree', ['$compile', function ($compile)
    {
        return {
            restrict    : 'E',
            templateUrl : 'templates/tree.html',
            transclude  : true,
            scope: {
                node         : '=',
                onToggleOpen : '&',
                toggleOpenFn : '='
            },
            compile: function(tElem, tAttr, transclude) {
                var contents = tElem.contents().remove();
                var compiledContents;
                return function (scope, iElem, iAttr) {
                    if (!compiledContents) {
                        compiledContents = $compile(contents, transclude);
                    }
                    compiledContents(scope, function (clone, scope) {
                        iElem.append(clone);
                    });
                }
            }
        };
    }]);

})(window, angular);

