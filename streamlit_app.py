# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App title
st.title(f"🧃 Customize Your Smoothie! 🧃 (Streamlit {st.__version__})")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name on Smoothie')
st.write('The name of your smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()
st.dataframe(data=my_dataframe, use_container_width=True)

# Multi-select for ingredients
ingredients_list = st.multiselect('Choose up to 5 Ingredients:', fruit_list, max_selections=5)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    # Insert order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}", icon="✅")

    # ✅ Show Nutrition Info for Each Fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        api_url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        smoothiefroot_response = requests.get(api_url)
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Could not fetch data for {fruit_chosen}")
