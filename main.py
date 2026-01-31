import re
import pandas as pd

def chat_text_to_df(text: str) -> pd.DataFrame:
    """
    Parse Meet Extension chat history text and return dataframe with:
    student_name, message_count, messages_concat (joined with '|')
    """

    # 1) Extract only the chat section (everything after Chat History)
    m = re.search(r"=+\s*Chat History\s*=+\s*(.*)", text, flags=re.DOTALL | re.IGNORECASE)
    chat_part = m.group(1) if m else text

    # 2) Each message line looks like:
    # Name > message...
    # We'll collect them
    pattern = re.compile(r"^\s*(.*?)\s*>\s*(.+?)\s*$")

    records = []
    for line in chat_part.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if match:
            name = match.group(1).strip()
            msg = match.group(2).strip()
            records.append((name, msg))

    df_raw = pd.DataFrame(records, columns=["student_name", "message"])

    if df_raw.empty:
        return pd.DataFrame(columns=["student_name", "message_count", "messages_concat"])

    # 3) Group by student and aggregate
    df_final = (
        df_raw.groupby("student_name", as_index=False)
        .agg(
            message_count=("message", "count"),
            messages_concat=("message", lambda x: " | ".join(x))
        )
        .sort_values("message_count", ascending=False)
        .reset_index(drop=True)
    )

    return df_final


if __name__ == "__main__":
    input_text = """PASTE YOUR FULL TEXT HERE"""
    df = chat_text_to_df(input_text)
    print(df)
    # df.to_csv("chat_summary.csv", index=False)
