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
        ['fileService', '$scope', '$rootScope', '$routeParams', '$sce',
            function (fileService, $scope, $rootScope, $routeParams, $sce)
    {
        fileService.getFile($routeParams.filename).then(function (file) {
            if (file.type == 'file') {
                $scope.contents = $sce.trustAsHtml(file.contents);
                $rootScope.$emit('fileOpened', $routeParams.filename);
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
        ['fileService', '$scope', '$rootScope', '$q',
            function (fileService, $scope, $rootScope, $q)
    {
        // Function for loading directory contents
        $scope.open = function (dir, parent) {

            var parentPath = parent === undefined ? '' : parent.path + '/';
            var path = parentPath + dir;
            return fileService.getFile(path).then(function (node) {
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
                    return node;
                } else {
                    return $q.reject([path + ' is not a directory']);
                }
            }).catch(function (errors) {
                //TODO: pass errors to message controller
                console.log(errors);
            });
        };

        // Function for recursively opening a path
        $scope.openPath = function (path, parent) {
            if (parent === undefined) {
                parent = $scope.root;
            }
            var segments = path.split('/');
            var segment = segments.shift();
            if (segment == '') {
                return;
            }
            if (parent.subdirs !== undefined
                    && parent.subdirs[segment] !== undefined) {
                parent.subdirs[segment].isOpen = true;
                $scope.openPath(segments.join('/'), parent.subdirs[segment]);
            } else {
                $scope.open(segment, parent).then(function (node) {
                    $scope.openPath(segments.join('/'), node);
                });
            }
        }

        // Function called from tree directive to expand / collapse directories
        $scope.toggleOpen = function (dir, parent) {

            // Check if dir contents are already loaded
            if (parent !== undefined
                    && parent.subdirs !== undefined
                    && parent.subdirs[dir] !== undefined) {
                // Toggle openness
                parent.subdirs[dir].isOpen = !parent.subdirs[dir].isOpen;
            } else {
                // Not yet loaded -> call backend
                $scope.open(dir, parent);
            }
        };

        // Load root directory
        $scope.open('').then(function () {
            // Subscribe to file load event once root dir has opened
            $rootScope.$on('fileOpened', function (evt, filename) {
                $scope.openPath(
                    filename
                        .replace(/\/[^\/]+$/, '') // trim basename
                        .replace(/^\//, '')       // and leading slash
                );
            });
        });

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

