module.exports = function (grunt) {
	grunt.initConfig({
		watch: {
			options: { livereload: true },
			less: {
				files: "static/less/*",
				tasks: ["less"]
			}
		},
		less: {
			dist: {
				files: {
					'static/css/style.css': ['static/less/main.less']
				},
				options: {
					sourceMap: true,
					sourceMapFilename: 'static/css/style.css.map',
					sourceMapBasepath: '/',
					sourceMapRootpath: '/'
				}
			}
		}

	});
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-contrib-less');

	grunt.registerTask('all', [
		'less',
		'watch'
	]);

	grunt.registerTask('default', [
		'all'
	]);
};
