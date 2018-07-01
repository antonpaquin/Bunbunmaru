docker:
	docker build -t user/bunbunmaru:dev .

clean:
	rm -rf src/server/__pycache__ src/__pycache src/bunbunmaru/__pycache src/units/__pycache src/bunbunmaru.db src/scheduler.db src/units/kissmanga.db src/bunbunmaru_collector.log
