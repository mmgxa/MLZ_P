import mlflow
import numpy as np
import pandas as pd
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from sklearn import svm
from sklearn.metrics import balanced_accuracy_score, mean_squared_error
from sklearn.model_selection import train_test_split


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
def train_model(x_y, num_trials):
    X_train, X_test, y_train, y_test = x_y

    def objective(params):

        with mlflow.start_run():
            mlflow.set_tag("model", "svm")
            mlflow.log_params(params)
            clf = svm.SVC(probability=True, **params)
            clf.fit(X_train, y_train)

            y_predict = clf.predict(X_test)
            acc = balanced_accuracy_score(y_test, y_predict)
            rmse = mean_squared_error(y_test, y_predict, squared=False)
            mlflow.log_metric("acc", acc)

        return {"loss": rmse, "acc": acc, "status": STATUS_OK}

    search_space = {
        "C": hp.quniform("C", 0.01, 1.5, 0.01),
        "kernel": hp.choice("kernel", ["linear", "rbf"]),
        "random_state": 42,
    }

    rstate = np.random.default_rng(42)  # for reproducible results
    fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=num_trials,
        trials=Trials(),
        rstate=rstate,
    )


@flow(task_runner=SequentialTaskRunner())
def main(filename, max_evals):
    HPO_EXPERIMENT_NAME = "wine-svm"

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment(HPO_EXPERIMENT_NAME)

    x_y = data_preprocess(filename)
    train_model(x_y, max_evals)


main("winequality-white.csv", 50)
