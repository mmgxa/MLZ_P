import mlflow
import pandas as pd
from hyperopt import hp, space_eval
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from sklearn import svm
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import train_test_split

SPACE = {
    "C": hp.quniform("C", 0.01, 1.5, 0.01),
    # 'kernel': hp.choice('kernel', ['linear', 'rbf']),
    "random_state": 42,
}


@task
def data_preprocess(filename):
    df_total = pd.read_csv(filename, header=0, dtype=float, delimiter=";")

    numerical = ["alcohol", "volatile acidity", "sulphates"]
    X = df_total[numerical].values

    target = "quality"
    y = df_total[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return (X_train, X_test, y_train, y_test)


@task
def train_and_log_model(runs, x_y):
    X_train, X_test, y_train, y_test = x_y

    for run in runs:
        with mlflow.start_run():
            params = run.data.params
            kernel = params.pop("kernel")
            params = space_eval(SPACE, params)
            params["kernel"] = kernel
            mlflow.log_params(params)
            clf = svm.SVC(probability=True, **params)
            clf.fit(X_train, y_train)

            y_predict = clf.predict(X_test)

            # evaluate model on the test set
            test_acc = balanced_accuracy_score(y_test, y_predict)
            mlflow.log_metric("test_acc", test_acc)
            mlflow.sklearn.log_model(clf, artifact_path="models")


@task
def run_search(client, HPO_EXPERIMENT_NAME, log_top):
    experiment = client.get_experiment_by_name(HPO_EXPERIMENT_NAME)
    # retrieve the top_n model runs and log the models to MLflow
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=log_top,
        order_by=["metrics.acc DESC"],
    )

    return runs


@task
def reg_best_model(client, EXPERIMENT_NAME, log_top):

    # select the model with the highest accuracy
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=log_top,
        order_by=["metrics.test_acc DESC"],
    )[0]

    # register the best model
    mlflow.register_model(
        f"runs:/{best_run.info.run_id}/models", name="wine-svm-best-models"
    )
    return best_run


@flow(task_runner=SequentialTaskRunner())
def run(filename, top_n):
    HPO_EXPERIMENT_NAME = "wine-svm"
    EXPERIMENT_NAME = "wine-svm-best-models"

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment(EXPERIMENT_NAME)

    client = MlflowClient()

    runs = run_search(client, HPO_EXPERIMENT_NAME, top_n).result()
    x_y = data_preprocess(filename).result()
    train_and_log_model(runs, x_y).result()
    best_run = reg_best_model(client, EXPERIMENT_NAME, top_n).result()
    print(f"The run_id of the best model is: {best_run.info.run_id}")


run("winequality-white.csv", 5)
